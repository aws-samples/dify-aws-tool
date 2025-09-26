from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import boto3

import json

class AgentcoreCodeInterpreterTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        action_type = tool_parameters["action_type"]
        if action_type == "exec_code":
            result = self.exec_code(**tool_parameters)
        elif action_type == "exec_command":
            result = self.exec_command(**tool_parameters)
        else:
            result = {}
        yield self.create_json_message(result)


    def exec_code(self, code_interpreter_id, language, code, session_id=None, aws_ak=None, aws_sk=None, aws_region=None, **kwargs):
        error_msg = ""

        try:
            if not aws_ak or aws_sk or aws_region:
                data_client = boto3.client('bedrock-agentcore')
                if not session_id:
                    session_id = self.init_session(data_client, code_interpreter_id)
            else:
                data_client = boto3.client("bedrock-agentcore", aws_access_key_id=aws_ak, aws_secret_access_key=aws_sk, region_name=aws_region)
                if not session_id:
                    session_id = self.init_session(data_client, code_interpreter_id)

            arguments = {
                "language": language,
                "code": code
            }
            response = data_client.invoke_code_interpreter(
            **{
                "codeInterpreterIdentifier": code_interpreter_id,
                "name": "executeCode",
                "sessionId": session_id,
                "arguments": arguments
            })
        except Exception as e:
            error_msg = str(e)
        
        if error_msg:
            result = {"status": "error", "reason": str(error_msg)}
        else:
            result = {"status": "success", "session_id": session_id, "result": self.get_tool_result(response)}
        
        return result


    def exec_command(self, code_interpreter_id, command, session_id=None, aws_ak=None, aws_sk=None, aws_region=None, **kwargs):
        error_msg = ""
        
        try:
            if not aws_ak or aws_sk or aws_region:
                data_client = boto3.client('bedrock-agentcore')
                if not session_id:
                    session_id = self.init_session(data_client, code_interpreter_id)
            else:
                data_client = boto3.client("bedrock-agentcore", aws_access_key_id=aws_ak, aws_secret_access_key=aws_sk, region_name=aws_region)
                if not session_id:
                    session_id = self.init_session(data_client, code_interpreter_id)

            arguments = {
                "command": command
            }
            response = data_client.invoke_code_interpreter(
            **{
                "codeInterpreterIdentifier": code_interpreter_id,
                "name": "executeCommand",
                "sessionId": session_id,
                "arguments": arguments
            })
        except Exception as e:
            error_msg = str(e)
        
        if error_msg:
            result = {"status": "error", "reason": str(error_msg)}
        else:
            result = {"status": "success", "session_id": session_id, "result": self.get_tool_result(response)}
        
        return result


    def init_session(self, data_client, ci_id):
        try:
            response = data_client.start_code_interpreter_session(codeInterpreterIdentifier=ci_id, sessionTimeoutSeconds=900)
            session_id = response['sessionId']
        except Exception as e:
            raise
        return session_id


    def get_tool_result(self, response):
        try:
            if "stream" in response:
                event_stream = response["stream"]
                for event in event_stream:
                    if "result" in event:
                        result = event["result"]
                        return str(result)
        except Exception as e:
            return f"tool result error: {e}"