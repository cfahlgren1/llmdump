# stdlib features
from dataclasses import dataclass
from typing import Optional
from importlib.metadata import PackageNotFoundError, version

# Observers internal interfaces
from observers.observers.base import Record
from observers.stores.base import Store

# Actual dependencies
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, Tracer, Span
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


OTEL_NAMESPACE = "huggingface.co/observers"


def flatten_dict(d, prefix=""):
    """Flatten a python dictionary, turning nested keys into dotted keys"""
    flat = {}
    for k, v in d.items():
        if v:
            if type(v) is dict:
                if prefix:
                    flat.extend(flatten_dict(v, f"{prefix}.{k}"))
            else:
                if prefix:
                    flat[(f"{prefix}.{k}")] = v
                else:
                    flat[k] = v


def get_version():
    try:
        return version("observers")
    except PackageNotFoundError:
        return "unknown"


@dataclass
class OpenTelemetryStore(Store):
    """
    OpenTelemetry Store
    """

    # These are here largely to ease future refactors/conform to
    # the style of the other stores. They have defaults set in the constructor,
    # but, set here as well.
    tracer: Optional[Tracer] = None
    root_span: Optional[Span] = None
    connected: bool = False

    def __post_init__(self):
        # if we weren't called by the `connect` constructor, we still need to
        # `connect`, and the example construction uses the ObjectName() syntax
        if not self.connected:
            self.tracer, self.connected = OpenTelemetryStore._connect()
        # if we initialize a span here, then all subsequent 'add's can be
        # added to a continuous trace
        with self.tracer.start_as_current_span(f"{OTEL_NAMESPACE}.init") as span:
            span.set_attribute("connected", True)
            self.root_span = span

    def add(self, record: Record):
        """Add a new record to the store"""
        with trace.use_span(self.root_span):
            with self.tracer.start_as_current_span(f"{OTEL_NAMESPACE}.add") as span:
                # Split out to be easily edited if the record api changes
                event_fields = [
                    "assistant_message",
                    "completion_tokens",
                    "total_tokens",
                    "prompt_tokens",
                    "finish_reason",
                    "tool_calls",
                    "function_call",
                    "tags",
                    "properties",
                    "error",
                    "model",
                    "timestamp",
                    "id",
                ]
                for field in event_fields:
                    data = record.__getattribute__(field)
                    if data:
                        if type(data) is dict:
                            intermediate = flatten_dict(data, field)
                            for k, v in intermediate:
                                span.set_attribute(k, v)
                        else:
                            span.set_attribute(field, data)
                # Special case for `messages` as it is a list of dicts
                messages = [str(message) for message in record.messages]
                span.set_attribute("messages", messages)

    @classmethod
    def connect(cls):
        """Alternate constructor for OpenTelemetryStore"""
        tracer, connected = cls._connect()
        return cls(tracer, connected)

    @classmethod
    def _connect(cls):
        """Connect to the OpenTelemetry endpoint"""
        provider = TracerProvider(
            resource=Resource.create(
                {
                    "instrument.name": OTEL_NAMESPACE,
                    "instrument.version": get_version(),
                }
            ),
        )
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(provider)
        tracer = trace.get_tracer(OTEL_NAMESPACE)
        connected = True
        return (tracer, connected)

    def _init_table(self, record: "Record"):
        """Initialize the dataset (no op)"""
        # We don't usually do this in otel, a dataset is (typically)
        # initialized by writing to it, but, it's part of the Store interface.
