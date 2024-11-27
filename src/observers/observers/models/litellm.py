from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

from observers.observers.models.openai import wrap_openai
from observers.stores.duckdb import DuckDBStore

if TYPE_CHECKING:
    from observers.stores.datasets import DatasetsStore


# copy of openai wrap
def wrap_litellm(
    client: Callable,
    store: Optional[Union["DatasetsStore", DuckDBStore]] = None,
    tags: Optional[List[str]] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> Callable:
    """
    Wrap Litellm completion function to track API calls in a Store.

    Args:
        client: Litellm completion function
        store: Store instance for persistence. Creates new if None
        tags: Optional list of tags to associate with records
        properties: Optional dictionary of properties to associate with records
    """

    # Create a mock OpenAI-like client structure
    class ChatCompletions:
        def __init__(self, create_fn):
            self.create = create_fn

    class Chat:
        def __init__(self, completions):
            self.completions = completions

    class MockClient:
        def __init__(self, chat):
            self.chat = chat

        def __call__(self, *args, **kwargs):
            return client(*args, **kwargs)

    # Set up the wrapped client with OpenAI-like structure
    tracked_client = MockClient(
        Chat(ChatCompletions(wrap_openai(client, store, tags, properties)))
    )
    return tracked_client
