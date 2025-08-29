import os
import json
from contextlib import asynccontextmanager
from typing import Any, Dict, cast

import uvicorn
import logging
from fastapi import FastAPI, HTTPException, Request, Response, status
from vllm import LLM

def main() -> int:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # ---------------------- Application lifespan management --------------------- #

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """
        A context manager to manage the startup and shutdown of the FastAPI application.
        """
        logger.info("Starting up: Loading model and transformer...")
        
        model_name = "Qwen/Qwen3-Reranker-0.6B"
        app.state.llm = LLM(
            model=model_name,
            task="score",
            hf_overrides={
                "architectures": ["Qwen3ForSequenceClassification"],
                "classifier_from_token": ["no", "yes"],
                "is_original_qwen3_reranker": True,
            },
        )

        logger.info("Model and transformer loaded...")

        yield  # This yield separates startup and shutdown logic

        logger.info("Shutting down the application...")

    # ----------------------------- Rank logic ---------------------------- #

    def Rerank(queries: list[str], docs: list[str], app: FastAPI) -> list[float]:
        """
        qwen rank logic
        """

        try:
            instruction="Given a web search query, retrieve relevant passages that answer the query"
            prefix = '<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n'
            suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"

            query_template = "{prefix}<Instruct>: {instruction}\n<Query>: {query}\n"
            document_template = "<Document>: {doc}{suffix}"
            formatted_queries = [
                query_template.format(prefix=prefix, instruction=instruction, query=query) 
                for query in queries
            ]
            formatted_docs = [
                document_template.format(doc=doc, suffix=suffix) 
                for doc in docs
            ]

            outputs = app.state.llm.score(formatted_queries, formatted_docs)
            scores = [ output.outputs.score for output in outputs ]

            return scores

        except Exception as e:
            logger.error(f"Error during rerank: {str(e)}")
            raise HTTPException(status_code=500, detail="Error during rerank")

    # ----------------------------- Application setup ---------------------------- #

    app = FastAPI(title="query-docs rerank", lifespan=lifespan)

    @app.get("/ping")
    async def ping() -> Dict[str, str]:
        """
        Sagemaker sends a periodic GET request to /ping endpoint to check if the container is healthy.
        """
        return {"message": "ok"}

    @app.post("/invocations")
    async def invocations(request: Request) -> Response:
        """
        Endpoint for Sagemaker to send POST requests to for inference.
        """
        logger.info("Invoked with request...")

        body = await request.json()
        inputs = body.get("inputs")
        docs = body.get("docs")

        try:
            scores = Rerank(queries=inputs, docs=docs, app=app)
            
            results = []
            for i, score in enumerate(scores):
                results.append({
                    "query": inputs[i],
                    "document": docs[i],
                    "score": float(score)  # 确保分数是可序列化的浮点数
                })
    
            # 根据分数降序排序
            sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)

            # 返回原始分数和排序后的结果
            result = {
                "scores": scores.tolist() if hasattr(scores, 'tolist') else scores,
                "ranked_results": sorted_results
            }
            
            return Response(
                content=json.dumps(result),
                media_type="application/json",
                status_code=status.HTTP_200_OK,
            )

        except ValueError as error:
            logger.error(f"Validation error: {error}")
            raise HTTPException(status_code=400, detail=str(error))

        except Exception as error:
            logger.error(f"Error during invocation: {error}")
            raise HTTPException(status_code=500, detail="Error during invocation")

    uvicorn.run(app, port=8080, host="0.0.0.0", log_level="info")

    return 0


if __name__ == "__main__":
    main()