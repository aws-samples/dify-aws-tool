# -*- coding: utf-8 -*-
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import io
import sys
import uuid
import logging
import boto3
from typing import Optional
from urllib.parse import urlparse
# ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append('{}/../../..'.format(ROOT_DIR))
# sys.path.append('{}/../../../third_party/Matcha-TTS'.format(ROOT_DIR))
import torch
import torchaudio
import numpy as np
import requests
from cosyvoice.cli.cosyvoice import CosyVoice
from cosyvoice.utils.file_utils import load_wav
from pydantic import BaseModel, Field

logging.getLogger('cosyvoice-inference').setLevel(logging.WARNING)

BUCKET=
S3_Prefix=

s3_client = boto3.client('s3')

class SftRequest(BaseModel):
    tts_text: str
    role: str

class ZeroShotRequest(BaseModel):
    prompt_audio: str
    tts_text: str
    prompt_text: Optional[str] = None

class InstructRequest(BaseModel):
    tts_text: str
    role: str
    instruct_text: str

def validate_sft_request(data: dict) -> SftRequest:
    return SftRequest(**data)

def validate_zero_shot_request(data: dict) -> ZeroShotRequest:
    return ZeroShotRequest(**data)

def validate_instruct_request(data: dict) -> InstructRequest:
    return InstructRequest(**data)

def save_to_s3(output) -> str:
    local_file_name = f'{uuid.uuid4()}.mp3'
    buffer = io.BytesIO()

    # soundfile doesn't support M4A and MP3, so we use "sox_io"
    torchaudio.set_audio_backend("sox_io")
    torchaudio.save(buffer, output, 22050, format='mp3')
    
    s3_key = f'{S3_Prefix}{local_file_name}'
    s3_client.put_object(
        Body=buffer.getvalue(),
        Bucket=BUCKET,
        Key=s3_key,
        ContentType='audio/mp3'
    )
    return f"s3://{BUCKET}/{s3_key}"

def generate_presigned_url(s3_uri, expiration=3600):
    """
    Generate a presigned URL for the S3 object

    :param s3_uri: The S3 URI of the object
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    # Parse the S3 URI
    parsed_uri = urlparse(s3_uri)
    bucket_name = parsed_uri.netloc
    object_key = parsed_uri.path.lstrip('/')

    # Generate the presigned URL
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name, 'Key': object_key},
                                                    ExpiresIn=expiration)
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None

    return response

def get_audio(url):
    audio_bytes = requests.get(url).content
    buff = io.BytesIO(audio_bytes)
    return buff

class CosyVoiceService():
    def __init__(self, model_dir:str):
        self.cosyvoice = CosyVoice(model_dir)
        logging.info('cosyvoice service initialized')

    def list_avaliable_spks(self):
        return self.cosyvoice.list_avaliable_spks()

    def predict_fn(self, request):
        audio_chunks = []
        
        if isinstance(request, SftRequest):
            logging.info('sft_request inference request')
            for i, j in enumerate(self.cosyvoice.inference_sft(request.tts_text, request.role, stream=False)):
                audio_chunks.append(j['tts_speech'])
        elif isinstance(request, ZeroShotRequest):
            audio_buff = get_audio(url=request.prompt_audio)
            prompt_speech_16k = load_wav(audio_buff, 16000)
            if request.prompt_text:
                logging.info('zero_shot_request inference request')
                for i, j in enumerate(self.cosyvoice.inference_zero_shot(request.tts_text, request.prompt_text, prompt_speech_16k, stream=False)):
                    audio_chunks.append(j['tts_speech'])
                    # s3_uri = save_to_s3(i, j['tts_speech'], 22050)
                    # s3_uri_list.append(s3_uri)
            else:
                logging.info('cross_lingual_request inference request')
                for i, j in enumerate(self.cosyvoice.inference_cross_lingual(request.tts_text, prompt_speech_16k, stream=False)):
                    audio_chunks.append(j['tts_speech'])
        elif isinstance(request, InstructRequest):
            logging.info('instruct_request inference request')
            for i, j in enumerate(self.cosyvoice.inference_instruct(request.tts_text, request.role, request.instruct_text, stream=False)):
                audio_chunks.append(j['tts_speech'])
        else:
            raise RuntimeError(f"invalid type of request: {type(request)}")

        if audio_chunks:
            full_audio = torch.cat(audio_chunks, dim=1)
            s3_uri = save_to_s3(full_audio)
            s3_presign_url = generate_presigned_url(s3_uri)
            return s3_uri, s3_presign_url
        else:
            raise RuntimeError('Invalid parameter passed.')
