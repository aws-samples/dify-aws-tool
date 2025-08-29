# vLLM SageMaker Deployment(English)

Open the deploy_and_test.ipynb in the SageMaker notebook and execute it step by step. This will allow you to deploy the LLM using the vllm framework. The resulting endpoint can be directly integrated with Dify.

This endpoint is equivalent to the one obtained from deploying with [Model_hub](https://github.com/aws-samples/llm_model_hub).

If you need a different model, you'll need to modify the model_id in the deploy_and_test.ipynb file. If you're deploying in the China region, you'll need to resolve network issues on your own (for example, using domestic sources for pip).

# vLLM SageMaker 部署方式(中文)

在SageMaker notebook中打开deploy_and_test.ipynb，一步一步执行，即可以按照vllm的方式部署LLM，获得的endpoint可以直接与Dify集成。

其与[Model_hub](https://github.com/aws-samples/llm_model_hub)部署得到的endpoint是等价的。

如果需要不同的模型，需要在deploy_and_test.ipynb中修改model_id，如果在中国区部署，需要自行解决网络的问题(比如pip使用境内的源)