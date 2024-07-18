import boto3
import json
import logging
from typing import Any, Union, List, Dict
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
    content: str = Field(..., description="The content to apply the guardrail to")
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

    def _apply_guardrail(self, params: GuardrailParameters) -> Dict[str, Any]:
        try:
            response = self.bedrockRuntimeClient.apply_guardrail(
                guardrailIdentifier=params.guardrail_id,
                guardrailVersion=params.guardrail_version,
                source=params.source,
                content=[{"text": {"text": params.content}}]
            )
            logger.info(f"Raw response from AWS: {json.dumps(response, indent=2)}")
            return response
        except ClientError as e:
            logger.error(f"AWS API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in _apply_guardrail: {str(e)}")
            raise

    def _invoke(self,
                user_id: str,
                tool_parameters: dict[str, Any]
                ) -> Union[ToolInvokeMessage, List[ToolInvokeMessage]]:
        """
        Invoke the ApplyGuardrail tool
        """
        try:
            # Validate and parse input parameters
            params = GuardrailParameters(**tool_parameters)
            
            # Initialize AWS client
            self._initialize_clients(params.aws_region)

            # Apply guardrail
            result = self._apply_guardrail(params)

            # Process the result
            action = result.get("action", "No action specified")
            outputs = result.get("outputs", [])
            assessments = result.get("assessments", [])
            
            output_text = "No output received"
            if outputs and isinstance(outputs, list) and len(outputs) > 0:
                output_text = outputs[0].get("text", "No specific output")

            assessment_text = "No assessments made"
            if assessments and isinstance(assessments, list) and len(assessments) > 0:
                assessment_text = json.dumps(assessments, indent=2)

            response_text = (
                f"Guardrail applied successfully.\n"
                f"Action: {action}\n"
                f"Output: {output_text}\n"
                f"Assessments: {assessment_text}\n"
                f"Full AWS response: {json.dumps(result, indent=2)}"
            )

            return self.create_text_message(text=response_text)

        except ValueError as e:
            return self.create_text_message(f'Invalid input parameters: {str(e)}')
        except ClientError as e:
            return self.create_text_message(f'AWS API error: {str(e)}')
        except Exception as e:
            logger.error(f"Unexpected error in _invoke: {str(e)}", exc_info=True)
            return self.create_text_message(f'An unexpected error occurred: {str(e)}')

    def create_text_message(self, text: str) -> ToolInvokeMessage:
        return ToolInvokeMessage(text=text, files=[], json=[])
