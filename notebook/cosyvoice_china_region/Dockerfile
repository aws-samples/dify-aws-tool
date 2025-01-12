FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

ARG MODEL_NAME=CosyVoice-300M-SFT
ENV MODEL_DIR=pretrained_models/${MODEL_NAME}

WORKDIR /opt/program

ENV PATH="/opt/program:${PATH}"
COPY code /opt/program

RUN apt-get update -y
RUN apt-get -y install git unzip git-lfs
RUN apt-get -y install sox libsox-dev

RUN git lfs install
RUN git clone https://www.modelscope.cn/iic/${MODEL_NAME}.git ${MODEL_DIR}

RUN git clone --recursive https://gitee.com/maccf/CosyVoice.git

RUN pip3 install orjson
RUN pip3 install boto3
RUN pip3 install ffmpeg-python
RUN cd CosyVoice && pip3 install -r requirements.txt

RUN ls
RUN chmod 755 serve