import boto3
import json
from typing import Any, Union, List
from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool

class ApplyGuardrailTool(BuiltinTool):
    bedrockRuntimeClient: Any = None
    bedrockClient: Any = None

    def _initialize_clients(self, region: str = "us-east-1"):
        if not self.bedrockRuntimeClient:
            self.bedrockRuntimeClient = boto3.client('bedrock-runtime', region_name=region)
        if not self.bedrockClient:
            self.bedrockClient = boto3.client('bedrock', region_name=region)

    def _apply_guardrail(self, guardrail_id: str, guardrail_version: str, source: str, text: str) -> dict:
        response = self.bedrockRuntimeClient.apply_guardrail(
            guardrailIdentifier=guardrail_id,
            guardrailVersion=guardrail_version, 
            source=source, 
            content=[{"text": {"text": text}}]
        )
        return response

    def _invoke(self, 
                user_id: str, 
                tool_parameters: dict[str, Any]
        ) -> Union[ToolInvokeMessage, List[ToolInvokeMessage]]:
        """
        Invoke the ApplyGuardrail tool
        """
        line = 0
        try:
            self._initialize_clients(tool_parameters.get('aws_region', 'us-east-1'))

            required_params = ['guardrail_id', 'guardrail_version', 'source', 'text']
            for param in required_params:
                line += 1
                if not tool_parameters.get(param):
                    return self.create_text_message(f'Please input {param}')

            line += 1
            result = self._apply_guardrail(
                tool_parameters['guardrail_id'],
                tool_parameters['guardrail_version'],
                tool_parameters['source'],
                tool_parameters['text']
            )

            action = result.get("action", "No action specified")
            output = result.get("outputs", [{}])[0].get("text", "No output received")

            response_text = f"Action: {action}\nOutput: {output}\nFull response: {json.dumps(result, indent=2)}"
            return self.create_text_message(text=response_text)

        except Exception as e:
            return self.create_text_message(f'Exception {str(e)}, line: {line}')