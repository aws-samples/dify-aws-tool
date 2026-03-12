# SGLang SageMaker 部署方案（简化版）

## 简介

本方案利用 **SGLang 原生的 SageMaker API 支持**来部署模型。SGLang v0.2.13+ 已经内置了 `/ping` 和 `/invocations` 端点，因此不需要额外的代理层。

## ✨ 关键特性

- ✅ **原生支持**：直接使用 SGLang 内置的 SageMaker 接口
- ✅ **简单部署**：单进程，无需代理层
- ✅ **快速启动**：架构简化，启动更快
- ✅ **易于维护**：代码清晰，调试方便
- ⚠️ **仅支持 Chat API**：`/invocations` 端点只支持 Chat Completions API（messages 格式）

## 架构

```
┌─────────────────────────────────────┐
│   SageMaker 请求 (端口 8080)        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   SGLang 服务器 (端口 8080)         │
│   • GET  /ping (原生支持)           │
│   • POST /invocations (原生支持)    │
│   • OpenAI 兼容 API                 │
└─────────────────────────────────────┘
```

## 快速开始

### 1. 构建镜像

在 SageMaker notebook 中打开 `deploy_and_test.ipynb`，执行构建步骤：

```python
MODEL_ID = "Qwen/Qwen3.5-0.8B"
INSTANCE_TYPE = "ml.g6.2xlarge"
SGLANG_VERSION = "v0.5.9"
```

执行 Cell 4 构建并推送镜像到 ECR（**只需执行一次**）。

### 2. 部署模型

按照 notebook 中的步骤进行部署：
- Cell 12-17：下载模型并上传到 S3
- Cell 19-20：创建启动脚本
- Cell 22-24：部署 SageMaker 端点

### 3. 测试

支持 Chat Completions API：
- Cell 28: Message API 非流式模式
- Cell 30: Message API 流式模式
