import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from openai._client import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from typing_extensions import Self

from observers.models.base import (
    AsyncChatCompletionObserver,
    ChatCompletionObserver,
    ChatCompletionRecord,
)
from observers.stores.datasets import DatasetsStore

if TYPE_CHECKING:
    from observers.stores.duckdb import DuckDBStore


class OpenAIRecord(ChatCompletionRecord):
    client_name: str = "openai"

    @classmethod
    def from_response(
        cls,
        response: Union[List[ChatCompletionChunk], ChatCompletion] = None,
        error=None,
        model=None,
        **kwargs,
    ) -> Self:
        """Create a response record from an API response or error"""
        if not response:
            return cls(finish_reason="error", error=str(error), **kwargs)

        # Handle streaming responses
        if isinstance(response, list):
            first_dump = response[0].model_dump()
            last_dump = response[-1].model_dump()
            content = ""

            completion_tokens = prompt_tokens = total_tokens = 0

            choices = last_dump.get("choices", [{}])[0]
            delta = choices.get("delta", {})

            raw_response = {}
            for i, r in enumerate(response):
                r_dump = r.model_dump()
                raw_response[i] = r_dump
                content += (
                    r_dump.get("choices", [{}])[0].get("delta", {}).get("content") or ""
                )
                usage = r_dump.get("usage", {}) or {}
                completion_tokens += usage.get("completion_tokens", 0)
                prompt_tokens += usage.get("prompt_tokens", 0)
                total_tokens += usage.get("total_tokens", 0)

            return cls(
                id=first_dump.get("id") or str(uuid.uuid4()),
                completion_tokens=completion_tokens,
                prompt_tokens=prompt_tokens,
                total_tokens=total_tokens,
                assistant_message=content,
                finish_reason=choices.get("finish_reason"),
                tool_calls=delta.get("tool_calls"),
                function_call=delta.get("function_call"),
                raw_response=raw_response,
                **kwargs,
            )

        # Handle non-streaming responses
        response_dump = response.model_dump()
        choices = response_dump.get("choices", [{}])[0].get("message", {})
        usage = response_dump.get("usage", {}) or {}
        return cls(
            id=response.id or str(uuid.uuid4()),
            completion_tokens=usage.get("completion_tokens"),
            prompt_tokens=usage.get("prompt_tokens"),
            total_tokens=usage.get("total_tokens"),
            assistant_message=choices.get("content"),
            finish_reason=response_dump.get("choices", [{}])[0].get("finish_reason"),
            tool_calls=choices.get("tool_calls"),
            function_call=choices.get("function_call"),
            raw_response=response_dump,
            **kwargs,
        )


def wrap_openai(
    client: Union[OpenAI, AsyncOpenAI],
    store: Optional[Union["DuckDBStore", DatasetsStore]] = None,
    tags: Optional[List[str]] = None,
    properties: Optional[Dict[str, Any]] = None,
    logging_rate: Optional[float] = 1,
) -> Union[ChatCompletionObserver, AsyncChatCompletionObserver]:
    """
    Wraps an OpenAI client in an observer.

    Args:
        client: The OpenAI client to wrap.
        store: The store to use to save the records.
        tags: The tags to associate with records.
        properties: The properties to associate with records.
        logging_rate: The logging rate to use for logging, defaults to 1
    """
    observer_args = dict(
        client=client,
        create=client.chat.completions.create,
        format_input=lambda inputs, **kwargs: {"messages": inputs, **kwargs},
        parse_response=OpenAIRecord.from_response,
        store=store,
        tags=tags,
        properties=properties,
        logging_rate=logging_rate,
    )

    if isinstance(client, AsyncOpenAI):
        return AsyncChatCompletionObserver(**observer_args)

    return ChatCompletionObserver(**observer_args)
