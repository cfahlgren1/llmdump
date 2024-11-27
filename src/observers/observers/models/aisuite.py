from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from observers.observers.models.openai import wrap_openai
from observers.stores.duckdb import DuckDBStore

if TYPE_CHECKING:
    from aisuite import Client

    from observers.stores.datasets import DatasetsStore


def wrap_aisuite(
    client: "Client",
    store: Optional[Union["DatasetsStore", DuckDBStore]] = None,
    tags: Optional[List[str]] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> "Client":
    """Wraps Aisuite client to track API calls in a Store.

    Args:
        client: Aisuite client instance
        store: Store for persistence (creates new if None)
        tags: Optional tags to associate with records
        properties: Optional properties to associate with records
    """
    return wrap_openai(client, store, tags, properties)
