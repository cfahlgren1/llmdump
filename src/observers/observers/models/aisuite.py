from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from observers.observers.models.openai import OpenAIResponseRecord
from observers.stores.duckdb import DuckDBStore

if TYPE_CHECKING:
    from aisuite import Client

    from observers.stores.datasets import DatasetsStore


# copy of openai wrap
def wrap_aisuite(
    client: "Client",
    store: Optional[Union["DatasetsStore", DuckDBStore]] = None,
    tags: Optional[List[str]] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> "Client":
    """
    Wrap OpenAI client to track API calls in a Store.

    Args:
        client: OpenAI client instance
        store: Store instance for persistence. Creates new if None
        tags: Optional list of tags to associate with records
        properties: Optional dictionary of properties to associate with records
    """
    if store is None:
        store = DuckDBStore.connect()

    original_create = client.chat.completions.create

    def tracked_create(*args, **kwargs):
        try:
            response = original_create(*args, **kwargs)

            entry = OpenAIResponseRecord.create(
                response=response,
                messages=kwargs.get("messages"),
                model=kwargs.get("model"),
                tags=tags or [],
                properties=properties,
            )
            store.add(entry)
            return response

        except Exception as e:
            entry = OpenAIResponseRecord.create(
                error=e,
                messages=kwargs.get("messages"),
                model=kwargs.get("model"),
                tags=tags or [],
                properties=properties,
            )
            store.add(entry)
            raise

    client.chat.completions.create = tracked_create
    return client
