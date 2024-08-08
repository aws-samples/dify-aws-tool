# Set inference model
# export MODEL_DIR=pretrained_models/CosyVoice-300M-Instruct
# For development
# fastapi dev api_server.py
# For production deployment
# fastapi run 6006 api_server.py

import os
import sys
import io,time
from time import sleep
import uvicorn
from datetime import datetime
import logging

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append('{}/CosyVoice'.format(ROOT_DIR))
sys.path.append('{}/CosyVoice/third_party/Matcha-TTS'.format(ROOT_DIR))
from inference import CosyVoiceService
from inference import validate_sft_request, validate_zero_shot_request, validate_instruct_request

model_dir = os.getenv("MODEL_DIR", "pretrained_models/CosyVoice-300M-SFT")

class LaunchFailed(Exception):
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    if model_dir:
        logging.info("MODEL_DIR is {}", model_dir)
        app.cosy_voice_service = CosyVoiceService(model_dir)
        # sft usage
        logging.info("Avaliable speakers {}", app.cosy_voice_service.list_avaliable_spks())
    else:
        raise LaunchFailed("MODEL_DIR environment must set")
    yield

app = FastAPI(lifespan=lifespan)

def inference_fn(data):
    request = None
    if model_dir == "pretrained_models/CosyVoice-300M-SFT":
        request = validate_sft_request(data)
    elif model_dir == "pretrained_models/CosyVoice-300M":
        request = validate_zero_shot_request(data)
    elif model_dir == "pretrained_models/CosyVoice-300M-Instruct":
        request = validate_instruct_request(data)
    else:
        return { "error" : f"invalid model_dir : {model_dir}" }

    audio_s3_uri, s3_presign_url = app.cosy_voice_service.predict_fn(request)
    logging.info(f"s3_presign_url: {s3_presign_url}")
    logging.info(f"audio_s3_uri: {audio_s3_uri}")
    return s3_presign_url

@app.get('/ping')
async def ping():
    return {"message": "ok"}

@app.post('/invocations')
async def invocations(request: Request):
    data = await request.json()
    s3_presign_url = inference_fn(data)
    return { "s3_presign_url": s3_presign_url }

@app.get('/roles')
async def roles():
    return {"roles": app.cosy_voice_service.list_avaliable_spks()}