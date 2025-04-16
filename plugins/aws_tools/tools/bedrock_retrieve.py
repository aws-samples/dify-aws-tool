import json
import operator
from typing import Any, Optional, Union
from collections.abc import Generator

import boto3

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class BedrockRetrieveTool(Tool):
    bedrock_client: Any = None
    knowledge_base_id: str = None
    topk: int = None

    def convert_to_dify_kb_format(self, kb_repsonse):
        result_array = []
        for idx, item in enumerate(kb_repsonse['retrievalResults']):
            # 提取基础字段
            source_uri = item['metadata']['x-amz-bedrock-kb-source-uri']
            page_number = item['metadata'].get('x-amz-bedrock-kb-document-page-number', 0)
            data_source_id = item['metadata'].get('x-amz-bedrock-kb-data-source-id', '')
            chunk_id = item['metadata'].get('x-amz-bedrock-kb-chunk-id','')
            score = item.get('score', 0.0)

            # 生成动态字段
            document_name = source_uri.split('/')[-1]

            # 构建元数据
            metadata = {
                "_source": "knowledge",
                "dataset_id": data_source_id,
                "dataset_name": "BedRock knowledge base",
                "document_id": document_name,
                "document_name": document_name,
                "document_data_source_type": item['content']['type'],
                "segment_id": chunk_id,
                "retriever_from": "workflow",
                "score": round(score, 6),
                "segment_hit_count": 1,  # 示例值递增
                "segment_word_count": len(item['content']['text']),  # 计算词数
                "segment_position": page_number,
                "doc_metadata": {
                    "tag": "bedrock knowledge base",
                    "source": item["location"]["type"],
                    "uploader": "advantage",
                    "upload_date": int(1715299200),  # 固定时间戳
                    "document_name": document_name,
                    "last_update_date": int(1715299200)
                },
                "position": idx + 1
            }

            if item['content']['text'].strip() != "" :
                result_array.append({
                    "content": item['content']['text'],
                    "title": f"{document_name}",  # 添加默认扩展名
                    "metadata": metadata
                })

        return result_array

    def _bedrock_retrieve(
        self,
        query_input: str,
        knowledge_base_id: str,
        num_results: int,
        search_type: str,
        rerank_model_id: str,
        metadata_filter: Optional[dict] = None,
    ):
        try:
            retrieval_query = {"text": query_input}

            if search_type not in ["HYBRID", "SEMANTIC"]:
                raise RuntimeException("search_type should be HYBRID or SEMANTIC")

            retrieval_configuration = {
                "vectorSearchConfiguration": {"numberOfResults": num_results, "overrideSearchType": search_type}
            }

            if rerank_model_id != "default":
                model_for_rerank_arn = f"arn:aws:bedrock:us-west-2::foundation-model/{rerank_model_id}"
                rerankingConfiguration = {
                    "bedrockRerankingConfiguration": {
                        "numberOfRerankedResults": num_results,
                        "modelConfiguration": {"modelArn": model_for_rerank_arn},
                    },
                    "type": "BEDROCK_RERANKING_MODEL",
                }

                retrieval_configuration["vectorSearchConfiguration"]["rerankingConfiguration"] = rerankingConfiguration
                retrieval_configuration["vectorSearchConfiguration"]["numberOfResults"] = num_results * 5

            # 如果有元数据过滤条件，则添加到检索配置中
            if metadata_filter:
                retrieval_configuration["vectorSearchConfiguration"]["filter"] = metadata_filter

            response = self.bedrock_client.retrieve(
                knowledgeBaseId=knowledge_base_id,
                retrievalQuery=retrieval_query,
                retrievalConfiguration=retrieval_configuration,
            )

            results = self.convert_to_dify_kb_format(response)

            return results
        except Exception as e:
            raise Exception(f"Error retrieving from knowledge base: {str(e)}")

    def _invoke(
        self,
        tool_parameters: dict[str, Any],
    ) -> Generator[ToolInvokeMessage]:
        """
        invoke tools
        """
        try:
            line = 0
            # Initialize Bedrock client if not already initialized
            if not self.bedrock_client:
                aws_region = tool_parameters.get("aws_region")
                aws_access_key_id = tool_parameters.get("aws_access_key_id")
                aws_secret_access_key = tool_parameters.get("aws_secret_access_key")

                client_kwargs = {"service_name": "bedrock-agent-runtime", "region_name": aws_region or None}

                # Only add credentials if both access key and secret key are provided
                if aws_access_key_id and aws_secret_access_key:
                    client_kwargs.update(
                        {"aws_access_key_id": aws_access_key_id, "aws_secret_access_key": aws_secret_access_key}
                    )

                self.bedrock_client = boto3.client(**client_kwargs)
        except Exception as e:
            yield self.create_text_message(f"Failed to initialize Bedrock client: {str(e)}")

        try:
            line = 1
            if not self.knowledge_base_id:
                self.knowledge_base_id = tool_parameters.get("knowledge_base_id")
                if not self.knowledge_base_id:
                    yield self.create_text_message("Please provide knowledge_base_id")

            line = 2
            if not self.topk:
                self.topk = tool_parameters.get("topk", 5)

            line = 3
            query = tool_parameters.get("query", "")
            if not query:
                yield self.create_text_message("Please input query")

            # 获取元数据过滤条件（如果存在）
            metadata_filter_str = tool_parameters.get("metadata_filter")
            metadata_filter = json.loads(metadata_filter_str) if metadata_filter_str else None

            search_type = tool_parameters.get("search_type")
            rerank_model_id = tool_parameters.get("rerank_model_id")

            line = 4
            retrieved_docs = self._bedrock_retrieve(
                query_input=query,
                knowledge_base_id=self.knowledge_base_id,
                num_results=self.topk,
                search_type=search_type,
                rerank_model_id=rerank_model_id,
                metadata_filter=metadata_filter,
            )

            line = 5
            result_type = tool_parameters.get("result_type")
            if result_type == "json":
                json_result = { "results" : retrieved_docs }
                yield self.create_json_message(json_result)
            else:
                text = ""
                for i, res in enumerate(sorted_docs):
                    text += f"{i + 1}: {res['content']}\n"
                yield self.create_text_message(text)

        except Exception as e:
            yield self.create_text_message(f"Exception {str(e)}, line : {line}")

    def validate_parameters(self, parameters: dict[str, Any]) -> None:
        """
        Validate the parameters
        """
        if not parameters.get("knowledge_base_id"):
            raise ValueError("knowledge_base_id is required")

        if not parameters.get("query"):
            raise ValueError("query is required")

        metadata_filter_str = parameters.get("metadata_filter")
        if metadata_filter_str and not isinstance(json.loads(metadata_filter_str), dict):
            raise ValueError("metadata_filter must be a valid JSON object")
