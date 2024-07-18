<p align="center">
    &nbsp<strong>简体中文</strong>&nbsp ｜ <a href="README.md"><strong>English</strong></a>&nbsp 
</p>
<br>

# Dify AWS Tool

## 简介
本仓库提供了一些示例代码,展示如何将 SageMaker Provider 和一些基于 AWS 服务的工具集成到 [Dify](https://github.com/langgenius/dify) 中。 

除了参考代码外,您还可以参考 Dify [官方指引](https://docs.dify.ai/guides/tools/quick-tool-integration) 获取更多信息。



## 前置条件

- Dify 环境

- AWS 账户和 AWS 使用经验

- 基本的 Linux 环境使用经验



## Assets 

***[注意]：欢迎大家贡献更多的workflow/sagemaker model/builtin tool, 可以fork本仓库提交merge request， 然后更新README.md， 自行在对应的表格新增一行***

#### Workflow 

| DSL Name                    | Description                                 | Link                                                  | Owner               |
| --------------------------- | ------------------------------------------- | ----------------------------------------------------- | ------------------- |
| Term_based_translate        | 集成了专词映射的翻译工作流                  | [DSL](./workflow/term_based_translation_workflow.yml) | ybalbert@amazon.com |
| Code_translate              | 不同代码种类之间的翻译工作流                | Coming                                                | binc@amazon.com     |
| Basic_RAG_Sample            | 最基础的RAG工作流示例，包含自定义rerank节点 | [DSL](basic_rag_sample.yml)                           | ybalbert@amazon.com |
| Andrewyng/translation-agent | 复刻吴恩达的tranlsate agent                 | [DSL](andrew_translation_agent.yml)                   | chuanxie@amazon.com |

#### Builtin_Tools

| Tool Name                 | Tool Type | Description       | Deploy_doc                                                   | Owner               |
| ------------------------- | --------- | ----------------- | ------------------------------------------------------------ | ------------------- |
| Rerank                    | PAAS      | 文本相似性排序    | [Notebook](https://raw.githubusercontent.com/aws-samples/dify-aws-tool/main/notebook/bge-embedding-m3-deploy.ipynb) | ybalbert@amazon.com |
| Term_multilingual_mapping | PAAS      | 切词/获取专词映射 | [Repo](https://github.com/ybalbert001/dynamodb-rag/tree/translate) | ybalbert@amazon.com |
| Bedrock Guardrails        | SAAS      | 文本审核过滤      | Coming                                                       | amyli@amazon.com    |

#### Model_Provider

| Model Name       | model_type          | Deploy_doc                                                   | Owner               |
| ---------------- | ------------------- | ------------------------------------------------------------ | ------------------- |
| Bge-m3-rerank-v2 | SageMaker\Rerank    | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/bge-embedding-m3-deploy.ipynb) | ybalbert@amazon.com |
| Bge-embedding-m3 | SageMaker\Embedding | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/bge-reranker-v2-m3-deploy.ipynb) | ybalbert@amazon.com |



## 安装方法

下面的脚本仅仅为了集成 SageMaker Model_provider 和 AWS Builtin Tools, 你可以从界面自行导入workflow.

```
dify_path=/home/ec2-user/dify
tag=aws

# step1 - 下载代码
git clone https://github.com/aws-samples/dify-aws-tool/

# step2 - 安装代码
mv ./dify-aws-tool/builtin_tools/aws ${dify_path}/api/core/tools/provider/builtin/
mv ./dify-aws-tool/model_provider/sagemaker ${dify_path}/api/core/model_runtime/model_providers/

# step3 - 构建docker镜像
cd ${dify_path}/api
sudo docker build -t dify-api:${tag} .

# step4 - 使用新镜像重启dify
# 修改 ${dify_path}/docker/docker-compose.yaml
# 把 api and worker 服务对应的镜像改成你刚刚构建的新镜像
cd ${dify_path}/docker/
sudo docker compose down
sudo docker compose up -d
```



## 如何部署SageMaker推理端点

如果您想将您的 Embedding/Rerank 模型添加到 Dify Sagemaker Model Provider,您应该首先在 Amazon SageMaker 中自行部署它们。详细参见[指引](./notebook/how_to_deploy.md).



## 目标受众
- Dify / AWS 用户
- 生成式 AI 开发者