import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

# Tricky import to avoid lazy loading of openai, useful for testing.
# TODO: find a better way to do this.
from openai._client import (
    AsyncOpenAI,
    OpenAI,
    OpenAIWithRawResponse,
    OpenAIWithStreamedResponse,
)
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
        response: Union[List[OpenAIWithStreamedResponse], OpenAIWithRawResponse] = None,
        error=None,
        **kwargs,
    ) -> Self:
        """Create a response record from an API response or error"""
        if not response:
            return cls(finish_reason="error", error=str(error), **kwargs)

        # Handle streaming responses
        if isinstance(response, list):
            model = response[0].model
            content = ""

            completion_tokens = 0
            prompt_tokens = 0
            total_tokens = 0

            finish_reason = response[-1].choices[0].finish_reason
            tool_calls = response[-1].choices[0].delta.tool_calls
            function_call = response[-1].choices[0].delta.function_call

            for r in response:
                content += r.choices[0].delta.content or ""
                usage = r.usage or {}
                completion_tokens += usage.get("completion_tokens", 0)
                prompt_tokens += usage.get("prompt_tokens", 0)
                total_tokens += usage.get("total_tokens", 0)

            return cls(
                id=response[0].id if response[0].id else str(uuid.uuid4()),
                model=model,
                completion_tokens=completion_tokens,
                prompt_tokens=prompt_tokens,
                total_tokens=total_tokens,
                assistant_message=content,
                finish_reason=finish_reason,
                tool_calls=tool_calls,
                function_call=function_call,
                raw_response={i: r.model_dump() for i, r in enumerate(response)},
                **kwargs,
            )

        # Handle non-streaming responses
        else:
            dump = response.model_dump()
            choices = dump.get("choices", [{}])[0].get("message", {})
            usage = dump.get("usage", {})
            model = kwargs.pop("model", dump.get("model"))
            return cls(
                id=response.id if response.id else str(uuid.uuid4()),
                model=model,
                completion_tokens=usage.get("completion_tokens"),
                prompt_tokens=usage.get("prompt_tokens"),
                total_tokens=usage.get("total_tokens"),
                assistant_message=choices.get("content"),
                finish_reason=dump.get("choices", [{}])[0].get("finish_reason"),
                tool_calls=choices.get("tool_calls"),
                function_call=choices.get("function_call"),
                raw_response=dump,
                **kwargs,
            )


def wrap_openai(
    client: Union[OpenAI, AsyncOpenAI],
    store: Optional[Union["DuckDBStore", DatasetsStore]] = None,
    tags: Optional[List[str]] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> Union[ChatCompletionObserver, AsyncChatCompletionObserver]:
    """
    Wraps an OpenAI client in an observer.

    Args:
        client (`Union[OpenAI, AsyncOpenAI]`):
            The OpenAI client to wrap.
        store (`Union[DuckDBStore, DatasetsStore]`, *optional*):
            The store to use to save the records.
        tags (`List[str]`, *optional*):
            The tags to associate with records.
        properties (`Dict[str, Any]`, *optional*):
            The properties to associate with records.
    """
    if isinstance(client, AsyncOpenAI):
        return AsyncChatCompletionObserver(
            client=client,
            create=client.chat.completions.create,
            format_input=lambda inputs, **kwargs: {"messages": inputs, **kwargs},
            parse_response=OpenAIRecord.from_response,
            store=store,
            tags=tags,
            properties=properties,
        )

    return ChatCompletionObserver(
        client=client,
        create=client.chat.completions.create,
        format_input=lambda inputs, **kwargs: {"messages": inputs, **kwargs},
        parse_response=OpenAIRecord.from_response,
        store=store,
        tags=tags,
        properties=properties,
    )
