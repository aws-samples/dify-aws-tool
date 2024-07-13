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



## How to deploy SageMaker Endpoint

If you want to add your Embedding/Rerank model to Dify Sagemaker Model Provider, you should deploy them by yourself in AWS/SageMaker at first.

- Access to Amazon SageMaker Notebook

    ![notebook](./snapshots/notebook_entry.png)

- Clone the below notebooks
    Enter the terminal, then run below script
    ```bash
    cd SageMaker/
    # download embedding model
    wget https://raw.githubusercontent.com/aws-samples/dify-aws-tool/dev/notebook/bge-embedding-m3-deploy.ipynb
    ## download rerank model
    wget https://raw.githubusercontent.com/aws-samples/dify-aws-tool/dev/notebook/bge-reranker-v2-m3-deploy.ipynb
    ```
- Run the cells of notebook Sequentially
    We prefer g4dn.xlarge(T4) GPU for embedding model and rerank model, and also please notice differences between China region and Global region.

- Check the Endpoints
  
  ![endpoint](./snapshots/endpoint_entry.png)
  


## How to use Tools in Dify

- Text Rerank Tool 
    - Deploy the SageMaker endpoint([bge-rerank-m3-v2](https://github.com/aws-samples/dify-aws-tool/blob/dev/notebook/bge-reranker-v2-m3-deploy.ipynb))
    - Orchestrate this tool like below snapshot
        ![Rerank](./snapshots/rerank.png)
- Term mapping Retrieval Tool (Translation scenario, based on Lambda and Dynamodb)
    - Deploy Repo [[dynamodb-rag](https://github.com/ybalbert001/dynamodb-rag/tree/translate)] 
    - Orchestrate this tool like below snapshot
        ![Term_Retrieval](./snapshots/term_retrieval.png)
    

## Target Audience

- Dify / AWS User
- GenAI Developer