1. Access to Amazon SageMaker Notebook

    ![notebook](../snapshots/notebook_entry.png)

2. Clone the below notebooks
    Enter the terminal, then run below script
    ```bash
    cd SageMaker/
    # download embedding model
    wget https://raw.githubusercontent.com/aws-samples/dify-aws-tool/main/notebook/bge-embedding-m3-deploy.ipynb
    ## download rerank model
    wget https://raw.githubusercontent.com/aws-samples/dify-aws-tool/main/notebook/bge-reranker-v2-m3-deploy.ipynb
    ```
3. Run the cells of notebook Sequentially
    We prefer g4dn.xlarge(T4) GPU for embedding model and rerank model, and also please notice differences between China region and Global region.

4. Check the Endpoints  ![endpoint](../snapshots/endpoint_entry.png)
