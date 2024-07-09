<p align="center">
    &nbsp<strong>English</strong>&nbsp ｜ <a href="README_ZH.md"><strong>简体中文</strong></a>&nbsp 
</p>
<br>

# Dify AWS Tools

## Introduction
This repo provide some sample code to show how to integrate some tools which based on AWS Service to [Dify](https://github.com/langgenius/dify). In addition to the reference code, you can also refer to the [official guide](https://docs.dify.ai/guides/tools/quick-tool-integration) for more information.

## How to Install
```
# step1 - download code
git clone https://github.com/aws-samples/dify-aws-tool/

# step2 - intall code
mv ./dify_aws-tool/builtin_tools/aws {dify_path}/api/core/tools/provider/builtin/
mv ./dify_aws-tool/model_provider/sagemaker {dify_path}/api/core/model_runtime/model_provider/

# step3 - build image
cd {dify_path}/api
sudo docker build -t dify-api:{tag} .

# step4 - restart dify with new image
# modify {dify_path}/docker/docker-compose.yaml
# change api and worker service's images to the image you just built
```

## Tools
- Text Rerank Tool (based on SageMaker)
    - sagemaker endpoint - deploy [notebook](https://github.com/aws-samples/private-llm-qa-bot/blob/main/notebooks/embedding/bge-reranker-v2-m3-deploy.ipynb)
    - snapshot
        ![Rerank](./rerank.png)
- Term mapping Retrieval Tool (Translation scenario, based on Lambda and Dynamodb)
    - Term-based Tranlation Repo - [dynamodb-rag](https://github.com/ybalbert001/dynamodb-rag/tree/translate)  
    - snapshot
    - ![Term_Retrieval](./term_retrieval.png)
    

## Prerequisites
- Dify Environment
- Some experience with AWS
- Basic experience with Linux environments
- Basic experience with Dify

## Target Audience
- Dify / AWS User
- GenAI Developer