import uuid
from dataclasses import asdict
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from typing_extensions import Self

from huggingface_hub import AsyncInferenceClient, InferenceClient
from observers.models.base import (
    AsyncChatCompletionObserver,
    ChatCompletionObserver,
    ChatCompletionRecord,
)
from observers.stores.datasets import DatasetsStore


if TYPE_CHECKING:
    from observers.stores.duckdb import DuckDBStore


class HFRecord(ChatCompletionRecord):
    client_name: str = "hf_client"

    @classmethod
    def from_response(cls, response=None, error=None, **kwargs) -> Self:
        """Create a response record from an API response or error"""
        if not response:
            return cls(finish_reason="error", error=str(error), **kwargs)

        choices = response.get("choices", [{}])[0].get("message", {})
        usage = response.get("usage", {})

        return cls(
            id=response.id if response.id else str(uuid.uuid4()),
            model=response.get("model"),
            completion_tokens=usage.get("completion_tokens"),
            prompt_tokens=usage.get("prompt_tokens"),
            total_tokens=usage.get("total_tokens"),
            assistant_message=choices.get("content"),
            finish_reason=response.get("choices", [{}])[0].get("finish_reason"),
            tool_calls=choices.get("tool_calls"),
            function_call=choices.get("function_call"),
            raw_response=asdict(response),
            **kwargs,
        )


def wrap_hf_client(
    client: Union[InferenceClient, AsyncInferenceClient],
    store: Optional[Union["DuckDBStore", DatasetsStore]] = None,
    tags: Optional[List[str]] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> ChatCompletionObserver:
    """
    Wraps Hugging Face's Inference Client in an observer.

    Args:
        client (`Union[InferenceClient, AsyncInferenceClient]`):
            The HF Inference Client to wrap.
        store (`Union[DuckDBStore, DatasetsStore]`, *optional*):
            The store to use to save the records.
        tags (`List[str]`, *optional*):
            The tags to associate with records.
        properties (`Dict[str, Any]`, *optional*):
            The properties to associate with records.
    """
    if isinstance(client, AsyncInferenceClient):
        return AsyncChatCompletionObserver(
            client=client,
            create=client.chat.completions.create,
            format_input=lambda inputs, **kwargs: {"messages": inputs, **kwargs},
            parse_response=HFRecord.from_response,
            store=store,
            tags=tags,
            properties=properties,
        )

    return ChatCompletionObserver(
        client=client,
        create=client.chat.completions.create,
        format_input=lambda inputs, **kwargs: {"messages": inputs, **kwargs},
        parse_response=HFRecord.from_response,
        store=store,
        tags=tags,
        properties=properties,
    )
