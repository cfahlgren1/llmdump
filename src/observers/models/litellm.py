from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import litellm

from observers.models.base import AsyncChatCompletionObserver, ChatCompletionObserver
from observers.models.openai import OpenAIRecord

if TYPE_CHECKING:
    from observers.stores.argilla import ArgillaStore
    from observers.stores.datasets import DatasetsStore
    from observers.stores.duckdb import DuckDBStore


def wrap_litellm(
    client: Union[litellm.completion, litellm.acompletion],
    store: Optional[Union["DatasetsStore", "DuckDBStore", "ArgillaStore"]] = None,
    tags: Optional[List[str]] = None,
    properties: Optional[Dict[str, Any]] = None,
    logging_rate: Optional[float] = 1,
) -> Union[AsyncChatCompletionObserver, ChatCompletionObserver]:
    """
    Wrap Litellm completion function to track API calls in a Store.

    Args:
        client (`Union[InferenceClient, AsyncInferenceClient]`):
            The HF Inference Client to wrap.
        store (`Union[DuckDBStore, DatasetsStore]`, *optional*):
            The store to use to save the records.
        tags (`List[str]`, *optional*):
            The tags to associate with records.
        properties (`Dict[str, Any]`, *optional*):
            The properties to associate with records.
        logging_rate (`float`, *optional*):
            The logging rate to use for logging, defaults to 1

    Returns:
        `Union[AsyncChatCompletionObserver, ChatCompletionObserver]`:
            The observer that wraps the Litellm completion function.
    """
    # Common observer arguments
    observer_args = dict(
        client=client,
        create=client,
        format_input=lambda inputs, **kwargs: {"messages": inputs, **kwargs},
        parse_response=OpenAIRecord.from_response,
        store=store,
        tags=tags,
        properties=properties,
        logging_rate=logging_rate,
    )

    # Return async or sync observer based on client type
    if client.__name__ == "acompletion":
        return AsyncChatCompletionObserver(**observer_args)

    return ChatCompletionObserver(**observer_args)
