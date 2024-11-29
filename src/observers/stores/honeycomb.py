# stdlib features
import os
from dataclasses import dataclass, field

# Observers internal interfaces
from observers.observers.base import Record
from observers.stores.base import Store

# Actual dependencies
import libhoney


@dataclass
class HoneycombStore(Store):
    """
    Honeycomb Store
    """

    # These are here largely to ease future refactors/conform to
    # the style of the other stores. They have defaults set in the constructor,
    # but, set here as well.
    api_key: str = field(default_factory=lambda: os.getenv("HONEYCOMB_API_KEY"))
    dataset: str = field(default_factory=lambda: os.getenv("HONEYCOMB_DATASET"))
    api_host: str = field(
        default_factory=lambda: os.getenv(
            "HONEYCOMB_API_ENDPOINT", default="https://api.honeycomb.io"
        )
    )
    connected: bool = False

    def __post_init__(self):
        # if we weren't called by the `connect` constructor, we still need to
        # `connect`, and the example construction uses the ObjectName() syntax
        if not self.connected:
            self.api_key, self.dataset, self.api_host, self.connected = (
                HoneycombStore._connect(self.api_key, self.dataset, self.api_host)
            )

    def add(self, record: Record):
        """Add a new record to the store"""
        # Split out to be easily edited if the record api changes
        event_data_map = {
            "messages": record.messages,
            "assistant_message": record.assistant_message,
            "completion_tokens": record.completion_tokens,
            "total_tokens": record.total_tokens,
            "prompt_tokens": record.prompt_tokens,
            "finish_reason": record.finish_reason,
            "tool_calls": record.tool_calls,
            "function_call": record.function_call,
            "tags": record.tags,
            "properties": record.properties,
            "error": record.error,
            "model": record.model,
            "timestamp": record.timestamp,
            "id": record.id,
        }
        event = libhoney.new_event()
        event.add(event_data_map)
        event.send()

    @classmethod
    def connect(cls, api_key=None, dataset=None, api_host=None):
        """Alternate constructor for HoneycombStore"""
        api_key, dataset, api_host, connected = cls._connect(api_key, dataset, api_host)
        return cls(api_key, dataset, api_host, connected)

    @classmethod
    def _connect(cls, api_key=None, dataset=None, api_host=None):
        """Connect to the Honeycomb Observability Platform"""
        if not api_key:
            api_key = os.getenv("HONEYCOMB_API_KEY")
            if not api_key:
                raise Exception("A Honeycomb API or Ingest key is required")
        if not dataset:
            dataset = os.getenv("HONEYCOMB_DATASET", default="huggingface-observers")
        if not api_host:
            api_host = os.getenv(
                "HONEYCOMB_API_ENDPOINT", default="https://api.honeycomb.io"
            )
        libhoney.init(writekey=api_key, dataset=dataset, api_host=api_host)
        connected = True
        return (api_key, dataset, api_host, connected)

    def _init_table(self, record: "Record"):
        """Initialize the dataset (no op)"""
        # We don't actually do this in Honeycomb, a dataset is (typically)
        # initialized by writing to it, but, it's part of the Store interface.
        pass
