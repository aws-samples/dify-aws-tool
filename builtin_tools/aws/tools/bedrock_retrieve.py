import json
import operator
from typing import Any, Union

import boto3

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool


class BedrockRetrieveTool(BuiltinTool):
    bedrock_client: Any = None
    knowledge_base_id: str = None
    topk: int = None

    def _bedrock_retrieve(self, query_input: str, knowledge_base_id: str, num_results: int):
        try:
            response = self.bedrock_client.retrieve(
                knowledgeBaseId=knowledge_base_id,
                retrievalQuery={
                    'text': query_input
                },
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': num_results
                    }
                }
            )

            results = []
            for result in response.get('retrievalResults', []):
                results.append({
                    'content': result.get('content', {}).get('text', ''),
                    'score': result.get('score', 0.0),
                    'metadata': result.get('metadata', {})
                })

            return results
        except Exception as e:
            raise Exception(f"Error retrieving from knowledge base: {str(e)}")

    def _invoke(
            self,
            user_id: str,
            tool_parameters: dict[str, Any],
    ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
        invoke tools
        """
        line = 0
        try:
            if not self.bedrock_client:
                aws_region = tool_parameters.get("aws_region")
                if aws_region:
                    self.bedrock_client = boto3.client('bedrock-agent-runtime', region_name=aws_region)
                else:
                    self.bedrock_client = boto3.client('bedrock-agent-runtime')

            line = 1
            if not self.knowledge_base_id:
                self.knowledge_base_id = tool_parameters.get("knowledge_base_id")
                if not self.knowledge_base_id:
                    return self.create_text_message("Please provide knowledge_base_id")

            line = 2
            if not self.topk:
                self.topk = tool_parameters.get("topk", 5)

            line = 3
            query = tool_parameters.get("query", "")
            if not query:
                return self.create_text_message("Please input query")

            line = 4
            retrieved_docs = self._bedrock_retrieve(
                query_input=query,
                knowledge_base_id=self.knowledge_base_id,
                num_results=self.topk
            )

            line = 5
            # Sort results by score in descending order
            sorted_docs = sorted(retrieved_docs, key=operator.itemgetter("score"), reverse=True)

            line = 6
            return [self.create_json_message(res) for res in sorted_docs]

        except Exception as e:
            return self.create_text_message(f"Exception {str(e)}, line : {line}")

    def validate_parameters(self, parameters: dict[str, Any]) -> None:
        """
        Validate the parameters
        """
        if not parameters.get("knowledge_base_id"):
            raise ValueError("knowledge_base_id is required")

        if not parameters.get("query"):
            raise ValueError("query is required")