import time
from typing import Optional, Any

# import cohere
import numpy as np
# from cohere.core import RequestOptions

from core.model_runtime.entities.model_entities import PriceType
from core.model_runtime.entities.text_embedding_entities import EmbeddingUsage, TextEmbeddingResult
from core.model_runtime.errors.invoke import (
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeConnectionError,
    InvokeError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)
from core.model_runtime.errors.validate import CredentialsValidateFailedError
from core.model_runtime.model_providers.__base.text_embedding_model import TextEmbeddingModel


class SageMakerEmbeddingModel(TextEmbeddingModel):
    """
    Model class for Cohere text embedding model.
    """
    sagemaker_client: Any = None

    def _invoke(self, model: str, credentials: dict,
                texts: list[str], user: Optional[str] = None) \
            -> TextEmbeddingResult:
        """
        Invoke text embedding model

        :param model: model name
        :param credentials: model credentials
        :param texts: texts to embed
        :param user: unique user id
        :return: embeddings result
        """
        # get model properties

        embeddings = [ [0.0] * 1024 for item in range(len(texts)) ]

        # calc usage
        usage = self._calc_response_usage(
            model=model,
            credentials=credentials,
            tokens=0
        )

        return TextEmbeddingResult(
            embeddings=embeddings,
            usage=usage,
            model=model
        )

    def get_num_tokens(self, model: str, credentials: dict, texts: list[str]) -> int:
        """
        Get number of tokens for given prompt messages

        :param model: model name
        :param credentials: model credentials
        :param texts: texts to embed
        :return:
        """
        return 0

    def validate_credentials(self, model: str, credentials: dict) -> None:
        """
        Validate model credentials

        :param model: model name
        :param credentials: model credentials
        :return:
        """
        try:
            print("validate_credentials ok....")
        except Exception as ex:
            raise CredentialsValidateFailedError(str(ex))

    def _calc_response_usage(self, model: str, credentials: dict, tokens: int) -> EmbeddingUsage:
        """
        Calculate response usage

        :param model: model name
        :param credentials: model credentials
        :param tokens: input tokens
        :return: usage
        """
        # get input price info
        input_price_info = self.get_price(
            model=model,
            credentials=credentials,
            price_type=PriceType.INPUT,
            tokens=tokens
        )

        # transform usage
        usage = EmbeddingUsage(
            tokens=tokens,
            total_tokens=tokens,
            unit_price=input_price_info.unit_price,
            price_unit=input_price_info.unit,
            total_price=input_price_info.total_amount,
            currency=input_price_info.currency,
            latency=time.perf_counter() - self.started_at
        )

        return usage

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
