<p align="center">
  <h1 align="center">Dify AWS Tool</h1>
  <p align="center">
    <a href="README_ZH.md"><strong>简体中文</strong></a> | <strong>English</strong> | <a href="README_JA.md"><strong>日本語</strong></a>
  </p>
</p>

<p align="center">
  <a href="https://github.com/langgenius/dify">
    <img src="https://img.shields.io/badge/Powered%20by-Dify-blue" alt="Powered by Dify">
  </a>
  <a href="https://aws.amazon.com/">
    <img src="https://img.shields.io/badge/Platform-AWS-orange" alt="Platform AWS">
  </a>
</p>

## 📑 Table of Contents

- [Repository Introduction](#-repository-introduction)
- [Prerequisites](#️-prerequisites)
- [Technical Resources](#-technical-resources)
  - [Workflows](#workflows-demo-page)
  - [Extension Tools](#extension-tools)
  - [Model Providers](#model-providers)
- [Usage Notes](#-usage-notes)
  - [Getting Help](#getting-help)
  - [How to Contribute](#how-to-contribute)
- [Additional Materials](#-additional-materials)
  - [Demo Videos](#demo-videos)
  - [Related Blogs/Documents](#related-blogsdocuments)
  - [Hands-on Labs](#hands-on-labs)

## 📋 Repository Introduction

This repository provides the source code for three plugins in [Dify](https://github.com/langgenius/dify): **Bedrock Model Provider**, **SageMaker Model Provider**, and **AWS Tools**, as well as related workflows and demos for reference by Dify users and AWS users.

## ⚙️ Prerequisites

- Dify environment (can be deployed with one click using AWS CloudFormation - [dify.yaml](./dify.yaml))
  For production deployment, please refer to solution example [Dify-on-EKS](https://github.com/aws-samples/solution-for-deploying-dify-on-aws)
- AWS account and AWS experience
- Basic Linux environment experience

## 🧰 Technical Resources

### Workflows ([Demo Page](./workflow/README.md))

| Name | Description | Link | Dependencies | Owner |
|------|-------------|------|-------------|-------|
| Term_based_translate | Translation workflow with term mapping | [DSL](./workflow/term_based_translation_workflow.yml) | Tool(Term mapping) | [ybalbert](ybalbert@amazon.com) |
| Code_translate | Translation workflow between different code types | [DSL](./workflow/claude3_code_translation.yml) | | [binc](binc@amazon.com) |
| Basic_RAG_Sample | Basic RAG workflow example with custom rerank node | [DSL](./workflow/basic_rag_sample.yml) | Tool(Rerank) | [ybalbert](ybalbert@amazon.com) |
| Andrewyng/translation-agent | Recreation of Andrew Ng's translate agent | [DSL](./workflow/andrew_translation_agent.yml) | | [ybalbert](ybalbert@amazon.com) |
| rag_based_bot_with_tts | RAG-based bot with voice response capability | [DSL](./workflow/rag_based_bot_with_tts.yml) | Tool(TTS) | [ybalbert](ybalbert@amazon.com) |
| s3_rag | simple s3-based rag, no vector db needed | [DSL](./workflow/s3_rag.yml) | S3 Operator | [ybalbert](ybalbert@amazon.com) |
| Marketing-copywriter | End-to-end marketing copywriting | [DSL](./workflow/marketing-copywriting.yml) | | [Lyson Ober](https://www.youtube.com/@lysonober) |
| Simple_Kimi | Simple DIY Kimi | [DSL](./workflow/simple_kimi.yml) | | [ybalbert](ybalbert@amazon.com) |
| SVG_Designer | SVG icon designer | [DSL](./workflow/svg_designer.yml) | | [Li Jigang](https://waytoagi.feishu.cn/wiki/TRlTwxCFJis292kNAzEc9D4BnvY) |
| Education_Question_Gen | Education scenario - question generator | [DSL](./workflow/edu_question_gen.yml) | | [chuanxie](chuanxie@amazon.com) |
| Apply_guardrails | Chat workflow with safety guardrails | [DSL](./workflow/apply_guardrails.yml) | | [amyli](amyli@amazon.com) |
| LLM-Finetuning-Dataflow | LLM fine-tuning data synthesis workflow | [DSL](./workflow/LLM-Finetuning-Dataflow-dify) | [finetuning-on-aws](https://github.com/tsaol/finetuning-on-aws/tree/main) | [caoliuh](caoliuh@amazon.com) |
| Image/Video Generation Workflow | Generate images and videos based on Amazon Nova Canvas and Reel | [DSL](./workflow/generate_image_video.yml) | | [alexwuu](alexwuu@amazon.com) |
| EKS Upgrade Planning | Collect EKS cluster information and generate upgrade plan | [DSL](./workflow/eks_upgrade_planning/eks_upgrade_planning.yml) | | [wxyan](wxyan@amazon.com) |
| Amazon S3 powered DMS with chatbot Capabilities| RAG-based bot for nextcloud integration | [DSL](./workflow/rag_based_chatbot_for_nextcloud.yml) | | [tanzhuaz](tanzhuaz@amazon.com) |
| ASR_Transcribe | Transcribe audio to text | [DSL](./workflow/ASR_Transcribe.yml) | | [ybalbert](ybalbert@amazon.com) |
| Image(Text)-2-Image Search | Image2Image & Text2Image Search | [DSL](./workflow/opensearch_img_search.yml) | OpenSearch Knn Retriever | [ybalbert](ybalbert@amazon.com) |
| MCP Server Integration  | MCP Server Integration Demo | [DSL](./workflow/mcp_server_integration.yml) |  | [ybalbert](ybalbert@amazon.com) |

> 💡 For more workflows, check out community websites: [dify101.com](https://dify101.com/), [difyshare.com](https://difyshare.com/), [Awesome-Dify-Workflow](https://github.com/svcvit/Awesome-Dify-Workflow)

### Extension Tools

| Tool Name | Tool Type | Description | Deployment Documentation | Owner |
|-----------|-----------|-------------|--------------------------|-------|
| Rerank | PAAS | Text similarity ranking | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/bge-reranker-v2-m3-deploy.ipynb) | [ybalbert](ybalbert@amazon.com) |
| TTS | PAAS | Text-to-speech synthesis | [Code](https://github.com/aws-samples/dify-aws-tool/tree/main/notebook/cosyvoice) | [ybalbert](ybalbert@amazon.com) |
| Bedrock Guardrails | SAAS | Text moderation tool implemented through Amazon Bedrock Guardrail's standalone ApplyGuardrail API | | [amyli](amyli@amazon.com) |
| Term_multilingual_mapping | PAAS | Word segmentation/term mapping | [Repo](https://github.com/ybalbert001/dynamodb-rag/tree/translate) | [ybalbert](ybalbert@amazon.com) |
| Image Translation Tool | PAAS | Translate text in images | Coming | [tangqy](tangqy@amazon.com) |
| Chinese Toxicity Detector | PAAS | Chinese harmful content detection | Coming | [ychchen](ychchen@amazon.com) |
| Transcribe Tool | SAAS | AWS transcribe service tool (ASR) | | [river xie](chuanxie@amazon.com) |
| Bedrock Retriever | PAAS | Amazon Bedrock knowledge base retrieval tool | | [ychchen](ychchen@amazon.com) |
| S3 Operator | SAAS | Read and write S3 bucket content, can return presigned URLs | | [ybalbert](ybalbert@amazon.com) |
| AWS Bedrock Nova Canvas | SAAS | Generate images based on Amazon Nova Canvas | | [alexwuu](alexwuu@amazon.com) |
| AWS Bedrock Nova Reel | SAAS | Generate videos based on Amazon Nova Reel | | [alexwuu](alexwuu@amazon.com) |
| OpenSearch Knn Retriever | PAAS | Retrieve data from OpenSearch using KNN method | [Notebook](https://github.com/aws-samples/dify-aws-tool/tree/main/notebook/search_img_by_img) | [ybalbert](ybalbert@amazon.com) |

### Model Providers

| Model Name | Model Type | Deployment Documentation | Owner |
|------------|------------|--------------------------|-------|
| Any open source LLM | SageMaker\LLM | [Model_hub](https://github.com/aws-samples/llm_model_hub) | [ybalbert](ybalbert@amazon.com) |
| Bge-m3-rerank-v2 | SageMaker\Rerank | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/bge-reranker-v2-m3-deploy.ipynb) | [ybalbert](ybalbert@amazon.com) |
| Bge-embedding-m3 | SageMaker\Embedding | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/bge-embedding-m3-deploy.ipynb) | [ybalbert](ybalbert@amazon.com) |
| CosyVoice | SageMaker\TTS | [Code](https://github.com/aws-samples/dify-aws-tool/tree/main/notebook/cosyvoice) | [ybalbert](ybalbert@amazon.com) |
| SenseVoice | SageMaker\ASR | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/funasr-deploy.ipynb) | [ybalbert](ybalbert@amazon.com) |

> **📌 Important Note**
>
> Dify's SageMaker LLM Provider can support most open-source models. We recommend using [Model_hub](https://github.com/aws-samples/llm_model_hub) to deploy these models. It's very user-friendly and supports no-code model fine-tuning and deployment. If you don't want to install [Model_hub](https://github.com/aws-samples/llm_model_hub), you can also refer to this [guide](https://github.com/aws-samples/dify-aws-tool/tree/main/notebook/llm_sagemaker_deploy) to deploy LLMs to SageMaker using vllm.
>
> If you want to add your Embedding/Rerank/ASR/TTS models to the Dify Sagemaker Model Provider, you should first deploy them in Amazon SageMaker. Please refer to the corresponding [notebooks](https://github.com/aws-samples/dify-aws-tool/tree/main/notebook) for deployment.

## 🔧 Usage Notes

### Getting Help

- Raise issues on the repository's Issues page
- Consult the internal Lark group

![qr](./QR_Lark.png)

### How to Contribute

- Fork this repository and submit a Merge Request
- Update README.md, adding your work (such as workflows or tools) to the appropriate table

## 📚 Additional Materials

### Demo Videos

- [Dify 1.0.0 Release & AWS Plugin Adaptation](https://aws.highspot.com/items/67c2e250ac191e72528d176d?lfrm=rhp.0)
- [How to Use DeepSeek Models on AWS in Dify? Only 5 Minutes](https://mp.weixin.qq.com/s/psY6m9xUNce4QIyksKvapg)
- [Dify and Model Hub Integration for Mainstream Open-Source Models](https://mp.weixin.qq.com/s/t023tUS7QGb9CzFK40YVYw)
- [Dify Native Content Review Extension API Calls Bedrock Guardrail to Build Responsible AI Applications](https://amazon.awsapps.com/workdocs-preview/index.html#/document/1c6e65aa34790cbcbdd74871369ca1b079f2eb5a3d044d614c6cf4f622f56468)
- [Three Steps to Build Kimi Based on the Latest Bedrock C3.5-V2](https://mp.weixin.qq.com/s/_2obKrn849a6jOxML_8Btw)
- [AWS Services as Tools Integrated into Dify](https://mp.weixin.qq.com/s/ZZK4Qh0kcnlZHIdO82nVZA)
- [Dify and SageMaker ASR/TTS Integration](https://mp.weixin.qq.com/s/g2aey251YPk-tekL1uc_nw)
- [EKS Upgrade Planning](https://github.com/user-attachments/assets/0e7250a2-362d-47ae-95d5-b4004f9b30f4)
- [Bedrock based ChatBot for Nextcloud](https://github.com/user-attachments/assets/06612c09-0773-41e3-9a34-31d3382fc4d1)

### Related Blogs/Documents

- [Using Amazon Bedrock Guardrail via API Extension in Dify to Add Content Review Safety Guardrails to Chat Applications](https://amzn-chn.feishu.cn/docx/PhNbdiDRDoj8vlxIDjAcKBlVncb)
- [Integrating Dify and AWS Services for More Flexible Translation Workflows](https://br5879sdns.feishu.cn/docx/Osehd7t5ZocVocxhtQycBHDCnfb)
- [Using DeepSeek Models on AWS in Dify](https://amzn-chn.feishu.cn/docx/BtLHdxaG5o9xL6xXZcyciZUCn0f)

### Hands-on Labs

- [Rapidly Build GenAI Apps with Dify](https://catalog.us-east-1.prod.workshops.aws/workshops/2c19fcb1-1f1c-4f52-b759-0ca4d2ae2522/zh-CN)
- [CDK Deployment Solution for Dify Community Version Based on EKS](https://github.com/aws-samples/solution-for-deploying-dify-on-aws)
