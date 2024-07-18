import json
import logging
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GuardrailParameters(BaseModel):
    guardrail_id: str = Field(..., description="The ID of the guardrail to apply")
    guardrail_version: str = Field(..., description="The version of the guardrail to apply")
    content: str = Field(..., description="The content to apply the guardrail to")
    aws_region: str = Field(default="us-east-1", description="The AWS region to use")
    aws_access_key_id: str = Field(default="", description="AWS access key ID")
    aws_secret_access_key: str = Field(default="", description="AWS secret access key")

class ApplyGuardrail:
    def __init__(self):
        self.bedrock_client = None

    def _initialize_clients(self, region: str, access_key_id: str = None, secret_access_key: str = None):
        """Initialize AWS clients."""
        if self.bedrock_client is None:
            session = boto3.Session(
                region_name=region,
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key
            )
            self.bedrock_client = session.client(service_name='bedrock-agent-runtime')
        logger.info("AWS clients initialized.")

    def _apply_guardrail(self, params: GuardrailParameters) -> dict:
        """Apply the guardrail using AWS Bedrock."""
        try:
            response = self.bedrock_client.apply_guardrail(
                guardrailId=params.guardrail_id,
                guardrailVersion=params.guardrail_version,
                content=params.content
            )
            logger.info(f"Guardrail applied successfully. Response: {response}")
            return response
        except ClientError as e:
            logger.error(f"Error applying guardrail: {e}")
            raise

    def run(self, parameters: Dict[str, Any]) -> str:
        """
        Run the ApplyGuardrail tool
        """
        logger.info(f"Starting run with parameters: {parameters}")
        try:
            # Validate and parse input parameters
            params = GuardrailParameters(**parameters)
            
            # Initialize AWS client
            self._initialize_clients(params.aws_region, params.aws_access_key_id, params.aws_secret_access_key)

            # Apply guardrail
            result = self._apply_guardrail(params)

            # Process the result
            action = result.get("action", "No action")
            outputs = result.get("outputs", [])
            assessments = result.get("assessments", [])
            
            if action == "NONE" and not outputs and not any(assessments):
                response_text = (
                    "The guardrail did not trigger any actions or produce any outputs. "
                    "This could mean that the provided content did not violate any rules, "
                    "or that the guardrail may not be configured correctly for this type of content."
                )
            else:
                output_text = outputs[0].get("text", "No specific output") if outputs else "No outputs generated"
                assessment_text = json.dumps(assessments, indent=2) if assessments else "No assessments made"
                response_text = f"Action: {action}\nOutput: {output_text}\nAssessments: {assessment_text}"

            logger.info(f"Finishing run, returning: {response_text}")
            return response_text

        except ValueError as e:
            error_message = f'Invalid input parameters: {str(e)}'
            logger.error(error_message)
            return error_message
        except ClientError as e:
            error_message = f'AWS API error: {str(e)}'
            logger.error(error_message)
            return error_message
        except Exception as e:
            error_message = f'An unexpected error occurred: {str(e)}'
            logger.error(error_message, exc_info=True)
            return error_message

# 使用示例
if __name__ == "__main__":
    guardrail = ApplyGuardrail()
    result = guardrail.run({
        "guardrail_id": "your_guardrail_id",
        "guardrail_version": "your_guardrail_version",
        "content": "Your content to check",
        "aws_region": "us-east-1",
        # 如果需要，提供 AWS 凭证
        # "aws_access_key_id": "your_access_key_id",
        # "aws_secret_access_key": "your_secret_access_key"
    })
    print(result)
