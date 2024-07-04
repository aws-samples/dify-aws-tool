from typing import Optional

# import cohere
# from cohere.core import RequestOptions

from core.model_runtime.entities.rerank_entities import RerankDocument, RerankResult
from core.model_runtime.errors.invoke import (
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeConnectionError,
    InvokeError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)
from core.model_runtime.errors.validate import CredentialsValidateFailedError
from core.model_runtime.model_providers.__base.rerank_model import RerankModel


class SageMakerRerankModel(RerankModel):
    """
    Model class for Cohere rerank model.
    """
    sagemaker_client: Any = None

    def _sagemaker_rerank(self, query_input: str, docs: list[str], rerank_endpoint:str):
        inputs = [query_input]*len(docs)
        response_model = self.sagemaker_client.invoke_endpoint(
            EndpointName=rerank_endpoint,
            Body=json.dumps(
                {
                    "inputs": inputs,
                    "docs": docs
                }
            ),
            ContentType="application/json",
        )
        json_str = response_model['Body'].read().decode('utf8')
        json_obj = json.loads(json_str)
        scores = json_obj['scores']
        return scores if isinstance(scores, list) else [scores]


    def _invoke(self, model: str, credentials: dict,
                query: str, docs: list[str], score_threshold: Optional[float] = None, top_n: Optional[int] = None,
                user: Optional[str] = None) \
            -> RerankResult:
        """
        Invoke rerank model

        :param model: model name
        :param credentials: model credentials
        :param query: search query
        :param docs: docs for reranking
        :param score_threshold: score threshold
        :param top_n: top n
        :param user: unique user id
        :return: rerank result
        """
        line = 0
        try:
            if len(docs) == 0:
                return RerankResult(
                    model=model,
                    docs=docs
                )

            line = 1
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

            line = 2
            print("credentials:")
            print(credentials)

            line = 3
            sagemaker_endpoint = credentials.get('sagemaker_endpoint', None)
            candidate_docs = []

            scores = self._sagemaker_rerank(query, docs, sagemaker_endpoint)
            for idx in range(len(candidate_docs)):
                candidate_docs.append({"content" : docs[idx], "score": scores[idx]})

            sorted_candidate_docs = sorted(candidate_docs, key=lambda x: x['score'], reverse=True)
            
            line = 4
            rerank_documents = []
            for idx, result in enumerate(sorted_candidate_docs):
                rerank_document = RerankDocument(
                    index=idx,
                    text=result.get('content'),
                    score=result.get('score', -100.0)
                )

                if score_threshold is not None:
                    if rerank_document.score >= score_threshold:
                        rerank_documents.append(rerank_document)
                else:
                    rerank_documents.append(rerank_document)

            return RerankResult(
                model=model,
                docs=rerank_documents
            )

        except Exception as e:
            return self.create_text_message(f'Exception {str(e)}, line : {line}')

    def validate_credentials(self, model: str, credentials: dict) -> None:
        """
        Validate model credentials

        :param model: model name
        :param credentials: model credentials
        :return:
        """
        try:
            self.invoke(
                model=model,
                credentials=credentials,
                query="What is the capital of the United States?",
                docs=[
                    "Carson City is the capital city of the American state of Nevada. At the 2010 United States "
                    "Census, Carson City had a population of 55,274.",
                    "The Commonwealth of the Northern Mariana Islands is a group of islands in the Pacific Ocean that "
                    "are a political division controlled by the United States. Its capital is Saipan.",
                ],
                score_threshold=0.8
            )
        except Exception as ex:
            raise CredentialsValidateFailedError(str(ex))

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
                cohere.errors.service_unavailable_error.ServiceUnavailableError
            ],
            InvokeServerUnavailableError: [
                cohere.errors.internal_server_error.InternalServerError
            ],
            InvokeRateLimitError: [
                cohere.errors.too_many_requests_error.TooManyRequestsError
            ],
            InvokeAuthorizationError: [
                cohere.errors.unauthorized_error.UnauthorizedError,
                cohere.errors.forbidden_error.ForbiddenError
            ],
            InvokeBadRequestError: [
                cohere.core.api_error.ApiError,
                cohere.errors.bad_request_error.BadRequestError,
                cohere.errors.not_found_error.NotFoundError,
            ]
        }


    def _invoke(self, 
                user_id: str, 
               tool_parameters: dict[str, Any], 
        ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
            invoke tools
        """
        line = 0
        try:
            if not self.sagemaker_client:
                aws_region = tool_parameters.get('aws_region', None)
                if aws_region:
                    self.sagemaker_client = boto3.client("sagemaker-runtime", region_name=aws_region)
                else:
                    self.sagemaker_client = boto3.client("sagemaker-runtime")

            line = 1
            if not self.sagemaker_endpoint:
                self.sagemaker_endpoint = tool_parameters.get('sagemaker_endpoint', None)

            line = 2
            if not self.topk:
                self.topk = tool_parameters.get('topk', 5)

            line = 3
            query = tool_parameters.get('query', '')
            if not query:
                return self.create_text_message('Please input query')
            
            line = 4
            candidate_texts = tool_parameters.get('candidate_texts', None)
            if not candidate_texts:
                return self.create_text_message('Please input candidate_texts')
            
            line = 5
            candidate_docs = json.loads(candidate_texts)
            docs = [ item.get('content', None) for item in candidate_docs ]

            line = 6
            scores = self._sagemaker_rerank(query_input=query, docs=docs, rerank_endpoint=self.sagemaker_endpoint)

            line = 7
            for idx in range(len(candidate_docs)):
                candidate_docs[idx]["score"] = scores[idx]

            line = 8
            sorted_candidate_docs = sorted(candidate_docs, key=lambda x: x['score'], reverse=True)

            line = 9
            results_str = json.dumps(sorted_candidate_docs[:self.topk], ensure_ascii=False)
            return self.create_text_message(text=results_str)
            
        except Exception as e:
            return self.create_text_message(f'Exception {str(e)}, line : {line}')