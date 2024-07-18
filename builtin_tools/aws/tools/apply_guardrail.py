import boto3
import json
import logging
from typing import Any, Union, List
from pydantic import BaseModel, Field
from botocore.exceptions import ClientError

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GuardrailParameters(BaseModel):
    guardrail_id: str = Field(..., description="The identifier of the guardrail")
    guardrail_version: str = Field(..., description="The version of the guardrail")
    source: str = Field(..., description="The source of the content")
    text: str = Field(..., description="The text to apply the guardrail to")
    aws_region: str = Field(default="us-east-1", description="AWS region for the Bedrock client")

class ApplyGuardrailTool(BuiltinTool):
    bedrockRuntimeClient: Any = None

    def _initialize_clients(self, region: str = "us-east-1"):
        if not self.bedrockRuntimeClient:
            try:
                self.bedrockRuntimeClient = boto3.client('bedrock-runtime', region_name=region)
            except Exception as e:
                logger.error(f"Failed to initialize Bedrock client: {str(e)}")
                raise
        return self.bedrockRuntimeClient

    def _invoke(self,
                user_id: str,
                tool_parameters: dict[str, Any]
                ) -> Union[ToolInvokeMessage, List[ToolInvokeMessage]]:
        """
        Invoke the ApplyGuardrail tool
        """
        line = 0
        try:
            # Validate and parse input parameters
            params = GuardrailParameters(**tool_parameters)
            
            # Initialize AWS client
            self._initialize_clients(params.aws_region)

            line = 1
            # Apply guardrail
            response = self.bedrockRuntimeClient.apply_guardrail(
                guardrailIdentifier=params.guardrail_id,
                guardrailVersion=params.guardrail_version,
                source=params.source,
                content=[{"text": {"text": params.text}}]
            )
            
            logger.info(f"Raw response from AWS: {json.dumps(response, indent=2)}")

            line = 2
            # Process the result
            action = response.get("action", "No action specified")
            output = response.get("outputs", [{}])[0].get("text", "No output received")
            assessments = response.get("assessments", [])

            line = 3
            # Format assessments
            formatted_assessments = []
            for assessment in assessments:
                for policy_type, policy_data in assessment.items():
                    if isinstance(policy_data, dict) and 'topics' in policy_data:
                        for topic in policy_data['topics']:
                            formatted_assessments.append(f"Policy: {policy_type}, Topic: {topic['name']}, Type: {topic['type']}, Action: {topic['action']}")
                    else:
                        formatted_assessments.append(f"Policy: {policy_type}, Data: {policy_data}")

            line = 4
            result = f"Action: {action}\n"
            result += f"Output: {output}\n"
            result += "Assessments:\n" + "\n".join(formatted_assessments) + "\n"
            result += f"Full response: {json.dumps(response, indent=2)}"

            return self.create_text_message(text=result)

        except ValueError as e:
            error_message = f'Invalid input parameters: {str(e)}, line: {line}'
            logger.error(error_message)
            return self.create_text_message(text=error_message)
        except ClientError as e:
            error_message = f'AWS API error: {str(e)}, line: {line}'
            logger.error(error_message)
            return self.create_text_message(text=error_message)
        except Exception as e:
            error_message = f'An unexpected error occurred: {str(e)}, line: {line}'
            logger.error(error_message, exc_info=True)
            return self.create_text_message(text=error_message)

    def create_text_message(self, text: str) -> ToolInvokeMessage:
        message = ToolInvokeMessage(text=text)
        logger.info(f"Created ToolInvokeMessage: {message}")
        return message
