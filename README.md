<p align="center">
    &nbsp<strong>English</strong>&nbsp ｜ <a href="README_ZH.md"><strong>简体中文</strong></a>&nbsp 
</p>
<br>

# Dify AWS Tool

## Introduction
This repo provides some sample code to show how to integrate SageMaker Provider and some AWS Service based tools to [Dify](https://github.com/langgenius/dify). 

In addition to the reference code, you can also refer to the [Dify official guide](https://docs.dify.ai/guides/tools/quick-tool-integration) for more information.



## Prerequisites

- Dify Environment

- AWS Account and AWS Experience

- Basic experience with Linux environments



## Assets 

***[Attention]：We welcome contributions of more workflows, SageMaker models, and built-in tools. You can fork this repository and submit a merge request, please also update README.md, you need to add a new row to the corresponding table***

#### Workflow 

| DSL Name                    | Description                                           | Link                                                  | Owner               |
| --------------------------- | ----------------------------------------------------- | ----------------------------------------------------- | ------------------- |
| Term_based_translate        | Translation Workflow with Term mapping Retrieval Tool | [DSL](./workflow/term_based_translation_workflow.yml) | ybalbert@amazon.com |
| Code_translate              | Code Transform between different Program Language     | Coming                                                | binc@amazon.com     |
| Basic_RAG_Sample            | simple basic rag workflow with rerank tool            | [DSL](basic_rag_sample.yml)                           | ybalbert@amazon.com |
| Andrewyng/translation-agent | Andrew Ng's translate agent.                          | [DSL](andrew_translation_agent.yml)                   | chuanxie@amazon.com |

#### Builtin_Tools

| Tool Name                 | Tool Type | Description                               | Deploy_doc                                                   | Owner               |
| ------------------------- | --------- | ----------------------------------------- | ------------------------------------------------------------ | ------------------- |
| Rerank                    | PAAS      | Text Similarity Rerank Tool               | [Notebook](https://raw.githubusercontent.com/aws-samples/dify-aws-tool/main/notebook/bge-embedding-m3-deploy.ipynb) | ybalbert@amazon.com |
| Term_multilingual_mapping | PAAS      | Word Segment/ Term mapping Retrieval Tool | [Repo](https://github.com/ybalbert001/dynamodb-rag/tree/translate) | ybalbert@amazon.com |
| Bedrock Guardrails        | SAAS      | Text moderation Tool                      | Coming                                                       | amyli@amazon.com    |

#### Model_Provider

| Model Name       | model_type          | Deploy_doc                                                   | Owner               |
| ---------------- | ------------------- | ------------------------------------------------------------ | ------------------- |
| Bge-m3-rerank-v2 | SageMaker\Rerank    | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/bge-embedding-m3-deploy.ipynb) | ybalbert@amazon.com |
| Bge-embedding-m3 | SageMaker\Embedding | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/bge-reranker-v2-m3-deploy.ipynb) | ybalbert@amazon.com |



## How to Install
Below Script is only for SageMaker Model_provider and AWS Builtin Tools,  you can import workflows from Web Interface.
```
dify_path=/home/ec2-user/dify
tag=aws

# step1 - download code
git clone https://github.com/aws-samples/dify-aws-tool/

# step2 - intall code
mv ./dify-aws-tool/builtin_tools/aws ${dify_path}/api/core/tools/provider/builtin/
mv ./dify-aws-tool/model_provider/sagemaker ${dify_path}/api/core/model_runtime/model_providers/

# step3 - build image
cd ${dify_path}/api
sudo docker build -t dify-api:${tag} .

# step4 - restart dify with new image
# [Todo] modify ${dify_path}/docker/docker-compose.yaml, change api and worker service's images to the image you just built
cd ${dify_path}/docker/
sudo docker compose down
sudo docker compose up -d
```



## How to deploy SageMaker Endpoint

If you want to add your Embedding/Rerank model to Dify Sagemaker Model Provider, you should deploy them by yourself in AWS/SageMaker at first.  Please see the [Guide](./notebook/how_to_deploy.md).



## Target Audience

- Dify / AWS User
- GenAI Developer