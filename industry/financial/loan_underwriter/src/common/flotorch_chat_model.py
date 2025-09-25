from typing import Any, Dict, List, Optional, Union
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.messages.utils import convert_to_openai_messages
from langchain_core.outputs import ChatResult, ChatGeneration
from flotorch.sdk.llm import FlotorchLLM
from config import settings


FLOTORCH_API_KEY = settings.flotorch_api_key
FLOTORCH_BASE_URL = settings.flotorch_base_url
FLOTORCH_MODEL = settings.flotorch_model


class ChatFloTorch(BaseChatModel):
    def __init__(
        self,
        client: Optional[FlotorchLLM] = None,
        *,
        api_key: str = FLOTORCH_API_KEY,
        base_url: str = FLOTORCH_BASE_URL,
        model_id: str = FLOTORCH_MODEL,
        default_params: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        """
        ChatFloTorch integrates LangChain with the FloTorch client.

        Args:
            client: Optionally provide your own FlotorchLLM instance.
            api_key, base_url, model_id: Optionally modify client config.
            default_params: Parameters merged into every request.
            **kwargs: Passed up to BaseChatModel.
        """
        super().__init__(**kwargs)

        # Use provided client or build a default one
        self._client = client or FlotorchLLM(
            api_key=api_key,
            base_url=base_url,
            model_id=model_id,
        )

        self._default_params = default_params or {}

    @property
    def _llm_type(self) -> str:
        return "flotorch"

    def convert_to_flotorch_messages(
        self,
        msgs: Union[BaseMessage, List[BaseMessage]]
    ) -> List[Dict[str, str]]:
        """
        Convert one or more LangChain BaseMessage into FloTorch format.
        """
        converted = convert_to_openai_messages(msgs)
        return converted if isinstance(converted, list) else [converted]
    
    
    def convert_to_langchain(self, response: Any) -> ChatResult:
        """
        Convert FloTorch response into LangChain ChatResult.
        Handles single or multiple generations.
        """
        generations: List[ChatGeneration] = []

        # If FloTorch returns multiple candidates
        if hasattr(response, "choices"):
            for choice in response.choices:
                generations.append(
                    ChatGeneration(message=AIMessage(content=choice.content))
                )

        # If FloTorch returns just one content field
        elif hasattr(response, "content"):
            generations.append(
                ChatGeneration(message=AIMessage(content=response.content))
            )

        else:
            raise ValueError(f"Unexpected FloTorch response format: {response}")

        return ChatResult(generations=generations)

    def _build_request(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs,
    ) -> tuple[list[dict[str, str]], dict[str, Any]]:
        """
        Prepare request and params for FloTorch client.
        """
        request = self.convert_to_flotorch_messages(messages)
        params = {**self._default_params, **kwargs}
        if stop is not None:
            params["stop"] = stop
        return request, params

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs,
    ) -> ChatResult:
        request, params = self._build_request(messages, stop, **kwargs)
        response = self._client.invoke(request, **params)
        result = self.convert_to_langchain(response)
        return result
        
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs,
    ) -> ChatResult:
        request, params = self._build_request(messages, stop, **kwargs)
        response = await self._client.ainvoke(request, **params)
        result = self.convert_to_langchain(response)
        return result


chat_llm = ChatFloTorch()