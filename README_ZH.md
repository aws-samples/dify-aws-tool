<p align="center">
    &nbsp<strong>简体中文</strong>&nbsp ｜ <a href="README.md"><strong>English</strong></a>&nbsp 
</p>
<br>

# Dify AWS Tool

## 简介
本仓库提供了一些示例代码,展示如何将 SageMaker Provider 和一些基于 AWS 服务的工具集成到 [Dify](https://github.com/langgenius/dify) 中。 

除了参考代码外,您还可以参考 Dify [官方指引](https://docs.dify.ai/guides/tools/quick-tool-integration) 获取更多信息。



## 前置条件

- Dify 环境 (可以通过AWS Cloudformation一键部署社区版 - [dify.yaml](./dify.yaml))

- AWS 账户和 AWS 使用经验

- 基本的 Linux 环境使用经验



## Assets 

***[注意]：欢迎大家贡献更多的workflow/sagemaker model/builtin tool, 可以fork本仓库提交merge request， 然后更新README.md， 自行在对应的表格新增一行***

#### 工作流 ([Demo页面](./workflow/README.md))

| 名称                        | 描述                                        | Link                                                  | 依赖                                                         | 负责人                                                       |
| --------------------------- | ------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Term_based_translate        | 集成了专词映射的翻译工作流                  | [DSL](./workflow/term_based_translation_workflow.yml) | Tool(专词映射)                                               | [ybalbert](ybalbert@amazon.com)                              |
| Code_translate              | 不同代码种类之间的翻译工作流                | [DSL](./workflow/claude3_code_translation.yml)        |                                                              | [binc](binc@amazon.com)                                      |
| Basic_RAG_Sample            | 最基础的RAG工作流示例，包含自定义rerank节点 | [DSL](./workflow/basic_rag_sample.yml)                | Tool(Rerank)                                                 | [ybalbert](ybalbert@amazon.com)                              |
| Andrewyng/translation-agent | 复刻吴恩达的tranlsate agent                 | [DSL](./workflow/andrew_translation_agent.yml)        |                                                              | [ybalbert](ybalbert@amazon.com)                              |
| rag_based_bot_with_tts      | 基于RAG能语音回答的Bot                      | [DSL](./workflow/rag_based_bot_with_tts.yml)          | Tool(TTS)                                                    | [ybalbert](ybalbert@amazon.com)                              |
| Marketing-copywriter        | 营销文案一条龙                              | [DSL](./workflow/marketing-copywriting.yml)           |                                                              | [Lyson Ober](https://www.youtube.com/@lysonober)             |
| Simple_Kimi                 | 简易自制Kimi                                | [DSL](./workflow/simple_kimi.yml)                     |                                                              | [ybalbert](ybalbert@amazon.com)                              |
| SVG_Designer                | SVG 图标设计师                              | [DSL](./workflow/svg_designer.yml)                    |                                                              | [李继刚](https://waytoagi.feishu.cn/wiki/TRlTwxCFJis292kNAzEc9D4BnvY) |
| Education_Question_Gen      | 教育场景 - 试题生成器                       | [DSL](./workflow/edu_question_gen.yml)                |                                                              | [chuanxie](chuanxie@amazon.com)                              |
| Apply_guardrails            | 应用安全防范的聊天工作流                    | [DSL](./workflow/apply_guardrails.yml)                |                                                              | [amyli](amyli@amazon.com)                                    |
| LLM-Finetuning-Dataflow     | LLM微调数据合成工作流                       | [DSL](./workflow/LLM-Finetuning-Dataflow-dify)        | [finetuning-on-aws](https://github.com/tsaol/finetuning-on-aws/tree/main) | [caoliuh](caoliuh@amazon.com)                                |
| Image/Video Generation Workflow   | 基于Amazon Nova Canvas和Reel生成图片和视频 | [DSL](./workflow/generate_image_video.yml)        |  | [alexwuu](alexwuu@amazon.com)               |

更多工作流可以关注社区网站：[dify101.com](https://dify101.com/); [difyshare.com](https://difyshare.com/); [Awesome-Dify-Workflow](https://github.com/svcvit/Awesome-Dify-Workflow)

#### 内置工具

| 工具名称                      | 工具类型 | 描述                                                                | 部署文档                                                     | 负责人                             |
|---------------------------| -------- |-------------------------------------------------------------------| ------------------------------------------------------------ |---------------------------------|
| Rerank                    | PAAS     | 文本相似性排序                                                           | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/bge-reranker-v2-m3-deploy.ipynb) | [ybalbert](ybalbert@amazon.com) |
| TTS                       | PAAS     | 语音合成                                                              | [Code](https://github.com/aws-samples/dify-aws-tool/tree/main/notebook/cosyvoice) | [ybalbert](ybalbert@amazon.com) |
| Bedrock Guardrails        | SAAS     | 文本审核工具，通过 Amazon Bedrock Guardrail 上提供的独立评估API ApplyGuardrail 来实现。 |                                                              | [amyli](amyli@amazon.com)       |
| Term_multilingual_mapping | PAAS     | 切词/获取专词映射                                                         | [Repo](https://github.com/ybalbert001/dynamodb-rag/tree/translate) | [ybalbert](ybalbert@amazon.com) |
| Image Translation Tool    | PAAS     | 翻译图片上的文字                                                          | Coming                                                      | [tanqy](tangqy@amazon.com)      |
| Chinese Toxicity Detector | PAAS     | 中文有害内容检测                                                          | Coming                                                      | [ychchen](ychchen@amazon.com)   |
| Transcribe Tool           | SAAS     | AWS transcribe service tool (ASR)                                 |                                                    | [river xie](chuanxie@amazon.com)      |
| Bedrock Retriever         | PAAS     | Amazon Bedrock知识库检索工具                                             |                                                       | [ychchen](ychchen@amazon.com)   |
| S3 Operator | SAAS | 读写S3中bucket的内容，可以返回presignURL | | [ybalbert](ybalbert@amazon.com) |
| AWS Bedrock Nova Canvas | SAAS | 基于Amazon Nova Canvas生成图像 | | [alexwuu](alexwuu@amazon.com) |
| AWS Bedrock Nova Reel | SAAS | 基于Amazon Nova Reel生成视频 | | [alexwuu](alexwuu@amazon.com) |
| OpenSearch Knn Retriever | PAAS | 用KNN方法从OpenSearch召回数据 | | [ybalbert](ybalbert@amazon.com) |

#### 模型提供商

| 模型名称         | 模型类型            | 部署文档                                                     | 负责人                          |
| ---------------- | ------------------- | ------------------------------------------------------------ | ------------------------------- |
| 任何开源模型     | SageMaker\LLM       | [Model_hub](https://github.com/aws-samples/llm_model_hub)    | [ybalbert](ybalbert@amazon.com) |
| Bge-m3-rerank-v2 | SageMaker\Rerank    | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/bge-reranker-v2-m3-deploy.ipynb) | [ybalbert](ybalbert@amazon.com) |
| Bge-embedding-m3 | SageMaker\Embedding | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/bge-embedding-m3-deploy.ipynb) | [ybalbert](ybalbert@amazon.com) |
| CosyVoice        | SageMaker\TTS       | [Code](https://github.com/aws-samples/dify-aws-tool/tree/main/notebook/cosyvoice) | [ybalbert](ybalbert@amazon.com) |
| SenseVoice       | SageMaker\ASR       | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/funasr-deploy.ipynb) | [ybalbert](ybalbert@amazon.com) |

**[注意]：Dify的SageMaker LLM Provider 可以支持大多数开源模型。我们建议您使用  [Model_hub](https://github.com/aws-samples/llm_model_hub). 来部署这些模型。它非常简单易用，支持无代码方式进行模型微调和部署。如果您不想安装[Model_hub](https://github.com/aws-samples/llm_model_hub)， 也可以参考[指引](https://github.com/aws-samples/dify-aws-tool/tree/main/notebook/llm_sagemaker_deploy)通过vllm的方式部署LLM到SageMaker**



## 安装方法

***下面的脚本仅仅为了集成 SageMaker Model_provider 和 AWS Builtin Tools, 你可以从界面自行导入workflow。 SageMaker 模型供应商已经被集成到Dify v0.6.15***

1. 设置变量
   ```bash
   dify_path=/home/ec2-user/dify #Please set the correct dify install path
   tag=aws
   ```

2. 下载代码
   ```bash
   cd /home/ec2-user/
   git clone https://github.com/aws-samples/dify-aws-tool.git
   ```
   
3. 安装代码
   ```bash
   # 请注意，很多模型和工具已经被默认集成到Dify，无需额外安装
   mv ./dify-aws-tool/builtin_tools/aws ${dify_path}/api/core/tools/provider/builtin/
   mv ./dify-aws-tool/model_provider/sagemaker ${dify_path}/api/core/model_runtime/model_providers/
   ```
   
4. 构建新镜像

   ```
   cd ${dify_path}/api
   sudo docker build -t dify-api:${tag} .
   ```

5. 为api和worker服务指定新镜像

   ```diff
   # 修改docker/docker-compose.yaml, 请参考下面的diff
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

5. 重启Dify
   ```bash
   cd ${dify_path}/docker/
   sudo docker-compose down
   sudo docker-compose up -d
   ```



## 如何部署SageMaker推理端点

如果您想将您的 LLM/Embedding/Rerank/ASR/TTS 模型添加到Dify Sagemaker Model Provider, 您应该首先在 Amazon SageMaker 中自行部署它们。
请参见对应的[notebook](https://github.com/aws-samples/dify-aws-tool#model_provider)去部署。

## 目标受众
- Dify / AWS 用户
- 生成式 AI 开发者

