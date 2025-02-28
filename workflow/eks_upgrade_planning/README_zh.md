# 基于LLM的EKS升级规划工具

本项目是一个利用大型语言模型(LLMs)生成Amazon Elastic Kubernetes Service (EKS)集群升级计划的工具。它使用`eks_cluster_info.py`脚本收集EKS集群信息，并将这些数据输入到`eks_upgrade_planning.yml`中定义的GenAI工作流中，以生成全面的升级计划。

## 概述

EKS升级规划工具由两个主要组件组成：

1. **EKS集群信息收集器(`eks_cluster_info.py`)**：一个Python脚本，用于收集EKS集群的详细信息，包括当前版本、健康状态、兼容性问题等。

2. **Dify工作流定义(`eks_upgrade_planning.yml`)**：一个工作流配置文件，定义了如何通过Claude (Anthropic的LLM)处理收集到的集群信息，以生成结构化的升级计划。

## 功能特点

- **全面的集群信息收集**：
  - 当前EKS版本
  - 集群健康问题
  - 与目标版本的兼容性问题
  - EKS插件兼容性
  - 版本偏差检测(kubelet, kube-proxy)
  - 已弃用API使用检测
  - 节点组和Fargate配置文件信息

- **智能升级规划**：
  - 特定版本的升级建议
  - 控制平面升级步骤
  - 数据平面(节点组)升级指导
  - 插件兼容性和升级路径
  - API版本迁移建议
  - 健康问题修复建议
  - 测试和验证指导

## 前提条件

- Python 3.6+
- 配置了适当EKS访问权限的AWS API客户端环境
- boto3库 1.36.26+
- 访问Dify平台以执行工作流

## 安装

1. 克隆此仓库或下载脚本文件。
2. 安装所需依赖：

   ```
   pip install -r requirements.txt
   ```

## 使用方法

### 步骤1：收集EKS集群信息

使用以下参数运行`eks_cluster_info.py`脚本：

- `cluster_name`：EKS集群名称
- `target_version`：用于兼容性检查的目标EKS版本
- `--region`（可选）：AWS区域
- `--profile`（可选）：要使用的AWS配置文件

示例：

```
python eks_cluster_info.py my-cluster 1.24 --region us-west-2
```

### 步骤2：将收集到的信息与Dify工作流一起使用

1. 复制`eks_cluster_info.py`脚本的输出。
2. 将`eks_upgrade_planning.yml`工作流定义导入到您的Dify实例中。
3. 在工作流中开始新的对话，并粘贴收集到的集群信息。
4. 选择目标EKS版本。
5. 工作流将处理信息并生成全面的升级计划。

## 工作流结构

`eks_upgrade_planning.yml`定义了一个Dify工作流，该工作流：

1. 从集群信息输入中提取参数
2. 获取相关的AWS文档作为参考
3. 分析升级的各个方面：
   - 集群健康问题
   - 插件兼容性
   - 特定版本的变更
   - 已弃用API的使用
   - 节点组和Fargate考虑因素
4. 为每个组件生成具有特定建议的结构化升级计划

## 输出

该工具生成一个全面的升级计划，包括：

- **集群信息摘要**
- **升级前检查**：
  - 特定版本的变更和建议
  - Kubelet和kube-proxy版本对齐
  - 插件兼容性检查
  - Kubernetes API版本兼容性
  - 集群健康检查和修复
- **控制平面升级步骤**
- **插件升级指导**
- **数据平面升级说明**
- **测试和验证建议**

## 注意事项

- 确保您的AWS凭证已正确配置，并具有足够的权限访问EKS资源。
- 该脚本使用AWS EKS的describe_cluster、list-insights和describe-insight等API获取兼容性信息，提供更准确和详细的见解。
- 该工具提供了全面的EKS集群信息收集和升级规划功能，可以根据特定需求进一步定制和扩展。

## 贡献

欢迎提出问题、建议或代码贡献以改进此工具。请随时创建问题或提交拉取请求。

## 许可证

本项目采用MIT许可证。有关详细信息，请参阅LICENSE文件。
