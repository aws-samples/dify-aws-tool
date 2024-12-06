<p align="center">
    &nbsp<strong>English</strong>&nbsp ｜ <a href="README_ZH.md"><strong>简体中文</strong></a>&nbsp 
</p>
<br>

# Dify AWS Tool

## Introduction
This repo provides some sample code to show how to integrate SageMaker Provider and some AWS Service based tools to [Dify](https://github.com/langgenius/dify). 

In addition to the reference code, you can also refer to the [Dify official guide](https://docs.dify.ai/guides/tools/quick-tool-integration) for more information.



## Prerequisites

- Dify Environment (It can be deployed on AWS with one click using Cloudformation Template - [dify.yaml](./dify.yaml))

- AWS Account and AWS Experience

- Basic experience with Linux environments



## Assets 

***[Attention]：We welcome contributions of more workflows, SageMaker models, and built-in tools. You can fork this repository and submit a merge request, please also update README.md, you need to add a new row to the corresponding table***

#### Workflow([Demo Page](./workflow/README.md))

| DSL Name                    | Description                                           | Link                                                  | Dependency         | Owner                                                        |
| --------------------------- | ----------------------------------------------------- | ----------------------------------------------------- | ------------------ | ------------------------------------------------------------ |
| Term_based_translate        | Translation Workflow with Term mapping Retrieval Tool | [DSL](./workflow/term_based_translation_workflow.yml) | Tool(Term_mapping) | [ybalbert](ybalbert@amazon.com)                              |
| Code_translate              | Code Transform between different Program Language     | [DSL](./workflow/claude3_code_translation.yml)        |                    | [binc](binc@amazon.com)                                      |
| Basic_RAG_Sample            | simple basic rag workflow with rerank tool            | [DSL](./workflow/basic_rag_sample.yml)                | Tool(Rerank)       | [ybalbert](ybalbert@amazon.com)                              |
| Andrewyng/translation-agent | Andrew Ng's translate agent.                          | [DSL](./workflow/andrew_translation_agent.yml)        |                    | [chuanxie](chuanxie@amazon.com)                              |
| rag_based_bot_with_tts      | Rag based bot which can answer with voice             | [DSL](./workflow/rag_based_bot_with_tts.yml)          | Tool(TTS)          | [ybalbert](ybalbert@amazon.com)                              |
| Marketing-copywriter        | marketing copywriter                                  | [DSL](./workflow/marketing-copywriting.yml)           |                    | [Lyson Ober](https://www.youtube.com/@lysonober)             |
| Simple_Kimi                 | Customized KIMI app                                   | [DSL](./workflow/simple_kimi.yml)                     |                    | [ybalbert](ybalbert@amazon.com)                              |
| SVG_Designer                | SVG Designer                                          | [DSL](./workflow/svg_designer.yml)                    |                    | [李继刚](https://waytoagi.feishu.cn/wiki/TRlTwxCFJis292kNAzEc9D4BnvY) |
| Education_Question_Gen      | Education Question Generator                          | [DSL](./workflow/edu_question_gen.yml)                |                    | [chuanxie](chuanxie@amazon.com)                              |
| Apply_guardrails            | Apply guardrails for chatbot                          | [DSL](./workflow/apply_guardrails.yml)                |                    | [amyli](amyli@amazon.com)                                    |

You can find more workflows on: [dify101.com](https://dify101.com/); [difyshare.com](https://difyshare.com/); [Awesome-Dify-Workflow](https://github.com/svcvit/Awesome-Dify-Workflow)

#### Builtin_Tools

| Tool Name                 | Tool Type  | Description                                                  | Deploy_doc                                                   | Owner                           |
| ------------------------- |------------| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------- |
| Rerank                    | PAAS       | Text Similarity Rerank Tool                                  | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/bge-reranker-v2-m3-deploy.ipynb) | [ybalbert](ybalbert@amazon.com) |
| TTS                       | PAAS       | Speech  synthesis Tool                                       | [Code](https://github.com/aws-samples/dify-aws-tool/tree/main/notebook/cosyvoice) | [ybalbert](ybalbert@amazon.com) |
| Bedrock Guardrails        | SAAS       | Text moderation Tool, implemented through the independent assessment API ApplyGuardrail API provided on Amazon Bedrock Guardrail. |                                                              | [amyli](amyli@amazon.com)       |
| Term_multilingual_mapping | PAAS       | Word Segment/ Term mapping Retrieval Tool                    | [Repo](https://github.com/ybalbert001/dynamodb-rag/tree/translate) | [ybalbert](ybalbert@amazon.com) |
| Image Translation Tool    | PAAS       | Translate the text on Image                                  | Coming                                                       | [tanqy](tangqy@amazon.com)      |
| Chinese Toxicity Detector | PAAS       | A tool to detect Chinese toxicity                             | Comming                                                      | [ychchen](ychchen@amazon.com)   |
| Transcribe Tool    | PAAS     | AWS transcribe service tool (ASR)                                        |                                                       | [river xie](chuanxie@amazon.com)      |

#### Model_Provider

| Model Name       | model_type          | Deploy_doc                                                   | Owner                           |
| ---------------- | ------------------- | ------------------------------------------------------------ | ------------------------------- |
| Any Model        | SageMaker\LLM       | [Model_hub](https://github.com/aws-samples/llm_model_hub)    | [ybalbert](ybalbert@amazon.com) |
| Bge-m3-rerank-v2 | SageMaker\Rerank    | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/bge-reranker-v2-m3-deploy.ipynb) | [ybalbert](ybalbert@amazon.com) |
| Bge-embedding-m3 | SageMaker\Embedding | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/bge-embedding-m3-deploy.ipynb) | [ybalbert](ybalbert@amazon.com) |
| CosyVoice        | SageMaker\TTS       | [Code](https://github.com/aws-samples/dify-aws-tool/tree/main/notebook/cosyvoice) | [ybalbert](ybalbert@amazon.com) |
| SenseVoice       | SageMaker\ASR       | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/funasr-deploy.ipynb) | [ybalbert](ybalbert@amazon.com) |

**[Attention]： The Dify provider of SageMaker\LLM can support most open-source models. We recommend you to reploy these models using [Model_hub](https://github.com/aws-samples/llm_model_hub). It's very easy and convenient which supports model fine-tuning and deployment with no-code approach**



## How to Install
***Below Script is only for SageMaker Model_provider and AWS Builtin Tools,  you can import workflows from Web Interface.  SageMaker Model_provider has already been integrated in Dify v0.6.15***
1. Set Env Variable
   ```bash
   dify_path=/home/ec2-user/dify #Please set the correct dify install path
   tag=aws
   ```

2. download code
   ```bash
   cd /home/ec2-user/
   git clone https://github.com/aws-samples/dify-aws-tool/
   ```
   
3. intall code
   ```bash
   # Part of models and tools have been integrated with dify already, no extra installation needed
   mv ./dify-aws-tool/builtin_tools/aws ${dify_path}/api/core/tools/provider/builtin/
   mv ./dify-aws-tool/model_provider/sagemaker ${dify_path}/api/core/model_runtime/model_providers/
   ```
   
4. build image

   ```
   cd ${dify_path}/api
   sudo docker build -t dify-api:${tag} .
   ```

5. Specify the new image for api and worker services

   ```diff
   # Modify docker/docker-compose.yaml, Please refer the below diff
   diff --git a/docker/docker-compose.yaml b/docker/docker-compose.yaml
   index cffaa5a6a..38538e5ca 100644
   --- a/docker/docker-compose.yaml
   +++ b/docker/docker-compose.yaml
   @@ -177,7 +177,7 @@ x-shared-env: &shared-api-worker-env
    services:
      # API service
      api:
   -    image: langgenius/dify-api:0.6.14
   +    image: dify-api:aws
        restart: always
        environment:
          # Use the shared environment variables.
   @@ -197,7 +197,7 @@ services:
      # worker service
      # The Celery worker for processing the queue.
      worker:
   -    image: langgenius/dify-api:0.6.14
   +    image: dify-api:aws
        restart: always
        environment:
          # Use the shared environment variables.
   ```

5. restart dify 
   ```bash
   cd ${dify_path}/docker/
   sudo docker-compose down
   sudo docker-compose up -d
   ```



## How to deploy SageMaker Endpoint

If you want to add your LLM/Embedding/Rerank/ASR/TTS model to Dify Sagemaker Model Provider, you should deploy them by yourself in AWS/SageMaker at first.  
Please refer the corresponding [notebook](https://github.com/aws-samples/dify-aws-tool#model_provider) to deploy.




## Target Audience

- Dify / AWS User
- GenAI Developer