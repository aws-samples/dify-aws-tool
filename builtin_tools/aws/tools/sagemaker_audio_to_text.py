import json
from typing import Any, Union
import boto3
import tempfile
import os
from urllib.parse import urlparse

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool


class WhisperTranscriptionTool(BuiltinTool):
    sagemaker_client: Any = None
    s3_client: Any = None
    sagemaker_endpoint: str = None

    def _get_s3_object_from_url(self, s3_url: str) -> tuple[str, str]:
        """从S3 URL解析出bucket和key"""
        parsed_url = urlparse(s3_url)
        bucket = parsed_url.netloc
        key = parsed_url.path.lstrip('/')
        return bucket, key

    def _download_from_s3(self, s3_url: str) -> str:
        """从S3下载文件到临时目录"""
        try:
            bucket, key = self._get_s3_object_from_url(s3_url)

            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_path = temp_file.name
            temp_file.close()

            # 下载文件
            self.s3_client.download_file(bucket, key, temp_path)

            return temp_path
        except Exception as e:
            raise Exception(f"从S3下载文件失败: {str(e)}")

    def _invoke_sagemaker(self, audio_data: bytes, endpoint: str):
        try:
            response = self.sagemaker_client.invoke_endpoint(
                EndpointName=endpoint,
                ContentType='audio/x-audio',
                Body=audio_data
            )
            response_body = response['Body'].read().decode('utf8')
            return response_body
        except Exception as e:
            raise Exception(f"转录失败: {str(e)}")

    def _invoke(self,
                user_id: str,
                tool_parameters: dict[str, Any],
                ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
        invoke tools
        """
        temp_file_path = None
        try:
            # 初始化 AWS 客户端
            if not self.sagemaker_client or not self.s3_client:
                aws_region = tool_parameters.get('aws_region')
                if aws_region:
                    self.sagemaker_client = boto3.client("sagemaker-runtime", region_name=aws_region)
                    self.s3_client = boto3.client('s3', region_name=aws_region)
                else:
                    self.sagemaker_client = boto3.client("sagemaker-runtime")
                    self.s3_client = boto3.client('s3')

            if not self.sagemaker_endpoint:
                self.sagemaker_endpoint = tool_parameters.get('sagemaker_endpoint')

            # 获取文件URL并下载
            file_url = tool_parameters.get('file_url')
            temp_file_path = self._download_from_s3(file_url)

            # 读取音频文件
            with open(temp_file_path, 'rb') as f:
                audio_data = f.read()

            # 调用 SageMaker 端点
            result = self._invoke_sagemaker(audio_data, self.sagemaker_endpoint)

            return self.create_text_message(text=result)

        except Exception as e:
            return self.create_text_message(f'Exception {str(e)}')
        finally:
            # 清理临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass