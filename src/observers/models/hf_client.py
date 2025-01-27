import uuid
from dataclasses import asdict
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from huggingface_hub import (
    AsyncInferenceClient,
    ChatCompletionOutput,
    ChatCompletionStreamOutput,
    InferenceClient,
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


class HFRecord(ChatCompletionRecord):
    client_name: str = "hf_client"

    @classmethod
    def from_response(
        cls,
        response: Union[
            None,
            List[ChatCompletionStreamOutput],
            ChatCompletionOutput,
        ] = None,
        error=None,
        **kwargs,
    ) -> Self:
        """Create a response record from an API response or error

        Args:
            response: The response from the API.
            error: The error from the API.
            **kwargs: Additional arguments passed to the observer.
        """
        if not response:
            return cls(finish_reason="error", error=str(error), **kwargs)

        # Handle streaming responses
        if isinstance(response, list):
            first_dump = asdict(response[0])
            last_dump = asdict(response[-1])
            id = first_dump.get("id") or str(uuid.uuid4())
            model = first_dump.get("model") or kwargs.get("model")

            choices = last_dump.get("choices", [{}])[0]
            delta = choices.get("delta", {})

            content = ""
            total_tokens = prompt_tokens = completion_tokens = 0
            raw_response = {}

            for i, r in enumerate(response):
                r_dump = asdict(r)
                raw_response[i] = r_dump
                usage = r_dump.get("usage", {})
                total_tokens += usage.get("total_tokens", 0)
                prompt_tokens += usage.get("prompt_tokens", 0)
                completion_tokens += usage.get("completion_tokens", 0)
                content += (
                    r_dump.get("choices", [{}])[0].get("delta", {}).get("content") or ""
                )

            return cls(
                id=id,
                model=model,
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
        response_dump = asdict(response)
        choices = response_dump.get("choices", [{}])[0].get("message", {})
        usage = response_dump.get("usage", {})

        return cls(
            id=response_dump.get("id") or str(uuid.uuid4()),
            model=response_dump.get("model"),
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


def wrap_hf_client(
    client: Union[InferenceClient, AsyncInferenceClient],
    store: Optional[Union["DuckDBStore", DatasetsStore]] = None,
    tags: Optional[List[str]] = None,
    properties: Optional[Dict[str, Any]] = None,
    logging_rate: Optional[float] = 1,
) -> Union[AsyncChatCompletionObserver, ChatCompletionObserver]:
    """
    Wraps Hugging Face's Inference Client in an observer.

    Args:
        client: The HF Inference Client to wrap.
        store: The store to use to save the records.
        tags: The tags to associate with records.
        properties: The properties to associate with records.
        logging_rate: The logging rate to use for logging, defaults to 1
    """
    observer_args = dict(
        client=client,
        create=client.chat.completions.create,
        format_input=lambda inputs, **kwargs: {"messages": inputs, **kwargs},
        parse_response=HFRecord.from_response,
        store=store,
        tags=tags,
        properties=properties,
        logging_rate=logging_rate,
    )

    if isinstance(client, AsyncInferenceClient):
        return AsyncChatCompletionObserver(**observer_args)

    return ChatCompletionObserver(**observer_args)
