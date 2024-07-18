from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field

from your_system_path import BuiltinTool

class GuardrailParameters(BaseModel):
    guardrail_id: str = Field(..., description="The ID of the guardrail to apply")
    guardrail_version: str = Field(..., description="The version of the guardrail to apply")
    content: str = Field(..., description="The content to apply the guardrail to")
    aws_region: str = Field(default="us-east-1", description="The AWS region to use")
    aws_access_key_id: str = Field(default="", description="AWS access key ID")
    aws_secret_access_key: str = Field(default="", description="AWS secret access key")

class ApplyGuardrail(BuiltinTool):
    name: str = "apply_guardrail"
    description: str = "Applies an AWS Bedrock guardrail to the given content"
    parameters: type[GuardrailParameters] = GuardrailParameters

    def __init__(self):
        super().__init__()
        self.bedrock_client = None

    def _initialize_client(self, region: str, access_key_id: str = None, secret_access_key: str = None):
        session = boto3.Session(
            region_name=region,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key
        )
        self.bedrock_client = session.client(service_name='bedrock-agent-runtime')

    def run(self, parameters: Dict[str, Any]) -> str:
        try:
            params = GuardrailParameters(**parameters)
            self._initialize_client(params.aws_region, params.aws_access_key_id, params.aws_secret_access_key)

            response = self.bedrock_client.apply_guardrail(
                guardrailId=params.guardrail_id,
                guardrailVersion=params.guardrail_version,
                content=params.content
            )

            action = response.get("action", "No action")
            outputs = response.get("outputs", [])
            assessments = response.get("assessments", [])

            if action == "NONE" and not outputs and not assessments:
                return "The guardrail did not trigger any actions or produce any outputs."

            output_text = outputs[0].get("text", "No specific output") if outputs else "No outputs generated"
            assessment_text = str(assessments) if assessments else "No assessments made"
            return f"Action: {action}\nOutput: {output_text}\nAssessments: {assessment_text}"

        except ValueError as e:
            return f'Invalid input parameters: {str(e)}'
        except ClientError as e:
            return f'AWS API error: {str(e)}'
        except Exception as e:
            return f'An unexpected error occurred: {str(e)}'
