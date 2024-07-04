import json
import logging
from collections.abc import Generator, Iterator
from typing import Optional, Union, cast, Any

# import cohere
# from cohere import (
#     ChatMessage,
#     ChatStreamRequestToolResultsItem,
#     GenerateStreamedResponse,
#     GenerateStreamedResponse_StreamEnd,
#     GenerateStreamedResponse_StreamError,
#     GenerateStreamedResponse_TextGeneration,
#     Generation,
#     NonStreamedChatResponse,
#     StreamedChatResponse,
#     StreamedChatResponse_StreamEnd,
#     StreamedChatResponse_TextGeneration,
#     StreamedChatResponse_ToolCallsGeneration,
#     Tool,
#     ToolCall,
#     ToolParameterDefinitionsValue,
# )
# from cohere.core import RequestOptions

from core.model_runtime.entities.llm_entities import LLMMode, LLMResult, LLMResultChunk, LLMResultChunkDelta
from core.model_runtime.entities.message_entities import (
    AssistantPromptMessage,
    PromptMessage,
    PromptMessageContentType,
    PromptMessageRole,
    PromptMessageTool,
    SystemPromptMessage,
    TextPromptMessageContent,
    ToolPromptMessage,
    UserPromptMessage,
)
from core.model_runtime.entities.model_entities import AIModelEntity, FetchFrom, I18nObject, ModelType
from core.model_runtime.errors.invoke import (
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeConnectionError,
    InvokeError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)
from core.model_runtime.errors.validate import CredentialsValidateFailedError
from core.model_runtime.model_providers.__base.large_language_model import LargeLanguageModel

logger = logging.getLogger(__name__)


class SageMakerLargeLanguageModel(LargeLanguageModel):
    """
    Model class for Cohere large language model.
    """
    sagemaker_client: Any = None

    def _invoke(self, model: str, credentials: dict,
                prompt_messages: list[PromptMessage], model_parameters: dict,
                tools: Optional[list[PromptMessageTool]] = None, stop: Optional[list[str]] = None,
                stream: bool = True, user: Optional[str] = None) \
            -> Union[LLMResult, Generator]:
        """
        Invoke large language model

        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param tools: tools for tool calling
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        :return: full response or stream response chunk generator result
        """
        # get model mode
        model_mode = self.get_model_mode(model, credentials)

        if not self.sagemaker_client:
            access_key = credentials.get('access_key', None)
            secret_key = credentials.get('secret_key', None)
            aws_region = credentials.get('aws_region', None)
            if aws_region:
                if access_key and secret_key:
                    self.sagemaker_client = boto3.client("sagemaker-runtime", 
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key,
                        region_name=aws_region)
                else:
                    self.sagemaker_client = boto3.client("sagemaker-runtime", region_name=aws_region)
            else:
                self.sagemaker_client = boto3.client("sagemaker-runtime")


        sagemaker_endpoint = credentials.get('sagemaker_endpoint', None)
        response_model = self.sagemaker_client.invoke_endpoint(
                    EndpointName=sagemaker_endpoint,
                    Body=json.dumps(
                    {
                        "inputs": prompt_messages[0].content,
                        "parameters": { "stop" : stop},
                        "history" : []
                    }
                    ),
                    ContentType="application/json",
                )

        assistant_text = response_model['Body'].read().decode('utf8')

        # transform assistant message to prompt message
        assistant_prompt_message = AssistantPromptMessage(
            content=assistant_text
        )

        usage = self._calc_response_usage(model, credentials, 0, 0)

        response = LLMResult(
            model=model,
            prompt_messages=prompt_messages,
            message=assistant_prompt_message,
            usage=usage
        )

        return response

    def get_num_tokens(self, model: str, credentials: dict, prompt_messages: list[PromptMessage],
                       tools: Optional[list[PromptMessageTool]] = None) -> int:
        """
        Get number of tokens for given prompt messages

        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param tools: tools for tool calling
        :return:
        """
        # get model mode
        model_mode = self.get_model_mode(model)

        try:
            return 0
        except Exception as e:
            raise self._transform_invoke_error(e)

    def validate_credentials(self, model: str, credentials: dict) -> None:
        """
        Validate model credentials

        :param model: model name
        :param credentials: model credentials
        :return:
        """
        try:
            # get model mode
            model_mode = self.get_model_mode(model)
        except Exception as ex:
            raise CredentialsValidateFailedError(str(ex))

    # def _convert_prompt_message_to_dict(self, message: PromptMessage) -> Optional[ChatMessage]:
    #     """
    #     Convert PromptMessage to dict for Cohere model
    #     """
    #     if isinstance(message, UserPromptMessage):
    #         message = cast(UserPromptMessage, message)
    #         if isinstance(message.content, str):
    #             chat_message = ChatMessage(role="USER", message=message.content)
    #         else:
    #             sub_message_text = ''
    #             for message_content in message.content:
    #                 if message_content.type == PromptMessageContentType.TEXT:
    #                     message_content = cast(TextPromptMessageContent, message_content)
    #                     sub_message_text += message_content.data

    #             chat_message = ChatMessage(role="USER", message=sub_message_text)
    #     elif isinstance(message, AssistantPromptMessage):
    #         message = cast(AssistantPromptMessage, message)
    #         if not message.content:
    #             return None
    #         chat_message = ChatMessage(role="CHATBOT", message=message.content)
    #     elif isinstance(message, SystemPromptMessage):
    #         message = cast(SystemPromptMessage, message)
    #         chat_message = ChatMessage(role="USER", message=message.content)
    #     elif isinstance(message, ToolPromptMessage):
    #         return None
    #     else:
    #         raise ValueError(f"Got unknown type {message}")

    #     return chat_message

    # def _convert_tools(self, tools: list[PromptMessageTool]) -> list[Tool]:
    #     """
    #     Convert tools to Cohere model
    #     """
    #     cohere_tools = []
    #     for tool in tools:
    #         properties = tool.parameters['properties']
    #         required_properties = tool.parameters['required']

    #         parameter_definitions = {}
    #         for p_key, p_val in properties.items():
    #             required = False
    #             if p_key in required_properties:
    #                 required = True

    #             desc = p_val['description']
    #             if 'enum' in p_val:
    #                 desc += (f"; Only accepts one of the following predefined options: "
    #                          f"[{', '.join(p_val['enum'])}]")

    #             parameter_definitions[p_key] = ToolParameterDefinitionsValue(
    #                 description=desc,
    #                 type=p_val['type'],
    #                 required=required
    #             )

    #         cohere_tool = Tool(
    #             name=tool.name,
    #             description=tool.description,
    #             parameter_definitions=parameter_definitions
    #         )

    #         cohere_tools.append(cohere_tool)

    #     return cohere_tools

    def _num_tokens_from_string(self, model: str, credentials: dict, text: str) -> int:
        """
        Calculate num tokens for text completion model.

        :param model: model name
        :param credentials: credentials
        :param text: prompt text
        :return: number of tokens
        """
        # initialize client
        client = cohere.Client(credentials.get('api_key'), base_url=credentials.get('base_url'))

        response = client.tokenize(
            text=text,
            model=model
        )

        return len(response.tokens)

    # def _num_tokens_from_messages(self, model: str, credentials: dict, messages: list[PromptMessage]) -> int:
    #     """Calculate num tokens Cohere model."""
    #     calc_messages = []
    #     for message in messages:
    #         cohere_message = self._convert_prompt_message_to_dict(message)
    #         if cohere_message:
    #             calc_messages.append(cohere_message)
    #     message_strs = [f"{message.role}: {message.message}" for message in calc_messages]
    #     message_str = "\n".join(message_strs)

    #     real_model = model
    #     if self.get_model_schema(model, credentials).fetch_from == FetchFrom.PREDEFINED_MODEL:
    #         real_model = model.removesuffix('-chat')

    #     return self._num_tokens_from_string(real_model, credentials, message_str)

    # def get_customizable_model_schema(self, model: str, credentials: dict) -> AIModelEntity:
    #     """
    #         Cohere supports fine-tuning of their models. This method returns the schema of the base model
    #         but renamed to the fine-tuned model name.

    #         :param model: model name
    #         :param credentials: credentials

    #         :return: model schema
    #     """
    #     # get model schema
    #     models = self.predefined_models()
    #     model_map = {model.model: model for model in models}

    #     mode = credentials.get('mode')

    #     if mode == 'chat':
    #         base_model_schema = model_map['command-light-chat']
    #     else:
    #         base_model_schema = model_map['command-light']

    #     base_model_schema = cast(AIModelEntity, base_model_schema)

    #     base_model_schema_features = base_model_schema.features or []
    #     base_model_schema_model_properties = base_model_schema.model_properties or {}
    #     base_model_schema_parameters_rules = base_model_schema.parameter_rules or []

    #     entity = AIModelEntity(
    #         model=model,
    #         label=I18nObject(
    #             zh_Hans=model,
    #             en_US=model
    #         ),
    #         model_type=ModelType.LLM,
    #         features=[feature for feature in base_model_schema_features],
    #         fetch_from=FetchFrom.CUSTOMIZABLE_MODEL,
    #         model_properties={
    #             key: property for key, property in base_model_schema_model_properties.items()
    #         },
    #         parameter_rules=[rule for rule in base_model_schema_parameters_rules],
    #         pricing=base_model_schema.pricing
    #     )

    #     return entity

    @property
    def _invoke_error_mapping(self) -> dict[type[InvokeError], list[type[Exception]]]:
        """
        Map model invoke error to unified error
        The key is the error type thrown to the caller
        The value is the error type thrown by the model,
        which needs to be converted into a unified error type for the caller.

        :return: Invoke error mapping
        """
        return {
            InvokeConnectionError: [
                RuntimeError
            ],
            InvokeServerUnavailableError: [
                RuntimeError
            ],
            InvokeRateLimitError: [
                RuntimeError
            ],
            InvokeAuthorizationError: [
                RuntimeError
            ],
            InvokeBadRequestError: [
                RuntimeError
            ]
        }
