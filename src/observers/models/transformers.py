import uuid
from typing import Any, Dict, List, Optional, Union

from typing_extensions import Self

import transformers
from observers.models.base import ChatCompletionObserver, ChatCompletionRecord
from observers.stores.datasets import DatasetsStore
from observers.stores.duckdb import DuckDBStore


class TransformersRecord(ChatCompletionRecord):
    """
    Data class for storing transformer records.
    """

    client_name: str = "transformers"

    @classmethod
    def from_response(
        cls,
        response: Dict[str, Any] = None,
        error: Exception = None,
        **kwargs,
    ) -> Self:
        if not response:
            return cls(finish_reason="error", error=str(error), **kwargs)
        generated_text = response[0]["generated_text"][-1]
        return cls(
            id=str(uuid.uuid4()),
            assistant_message=generated_text.get("content"),
            tool_calls=generated_text.get("tool_calls"),
            raw_response=response,
            **kwargs,
        )


def wrap_transformers(
    client: transformers.TextGenerationPipeline,
    store: Optional[Union[DuckDBStore, DatasetsStore]] = None,
    tags: Optional[List[str]] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> ChatCompletionObserver:
    """
    Wraps a transformers client in an observer.

    Args:
        client (`transformers.TextGenerationPipeline`):
            The transformers pipeline to wrap.
        store (`Union[DuckDBStore, DatasetsStore]`, *optional*):
            The store to use to save the records.
        tags (`List[str]`, *optional*):
            The tags to associate with records.
        properties (`Dict[str, Any]`, *optional*):
            The properties to associate with records.

    Returns:
        `ChatCompletionObserver`:
            The observer that wraps the transformers pipeline.
    """
    return ChatCompletionObserver(
        client=client,
        create=client.__call__,
        format_input=lambda inputs, **kwargs: {"text_inputs": inputs, **kwargs},
        parse_response=TransformersRecord.from_response,
        store=store,
        tags=tags,
        properties=properties,
    )
