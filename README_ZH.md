<p align="center">
    &nbsp<strong>简体中文</strong>&nbsp ｜ <a href="README.md"><strong>English</strong></a>&nbsp 
</p>
<br>

# Dify AWS Tools

## 简介
本仓库提供了一些示例代码，展示如何将基于 AWS 服务的一些工具集成到 [Dify](https://github.com/langgenius/dify) 中。 除了参考代码，你也可以参考[官方指引](https://docs.dify.ai/guides/tools/quick-tool-integration) 

## 如何安装
```
# step1 - 下载代码
git clone https://github.com/aws-samples/dify-aws-tool/

# step2 - 安装代码
mv ./dify_aws-tool/builtin_tools/aws {dify_path}/api/core/tools/provider/builtin/
mv ./dify_aws-tool/model_provider/sagemaker {dify_path}/api/core/model_runtime/model_provider/

# step3 - 构建docker镜像
cd {dify_path}/api
sudo docker build -t dify-api:{tag} .

# step4 - 使用新镜像重启dify
# modify {dify_path}/docker/docker-compose.yaml
# change api and worker service's images to the image you just built
```

## 工具
- 文本重排序工具（基于 SageMaker）
    - sagemaker endpoint - deploy [notebook](https://github.com/aws-samples/private-llm-qa-bot/blob/main/notebooks/embedding/bge-reranker-v2-m3-deploy.ipynb)
    - 工作流截图![重排序](./rerank.png)
    
- 术语映射检索工具（翻译场景，基于 Lambda 和 DynamoDB）
    - Term-based Tranlation Repo - [dynamodb-rag](https://github.com/ybalbert001/dynamodb-rag/tree/translate)  
    - 工作流截图![术语检索](./term_retrieval.png)


## 先决条件
- Dify 环境
- 具备一些 AWS 使用经验
- 具备 Linux 环境的基本使用经验
- 具备 Dify 的基本使用经验

## 目标受众
- Dify / AWS 用户
- 生成式 AI 开发者