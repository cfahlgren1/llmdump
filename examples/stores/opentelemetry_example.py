from observers.observers import wrap_openai
from observers.stores.opentelemetry import OpenTelemetryStore
from openai import OpenAI


# Use your usual environment variables to configure OpenTelemetry
# Here's an example for Honeycomb
# export OTEL_SERVICE_NAME=<identifiable-service-name>
# export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
# export OTEL_EXPORTER_OTLP_ENDPOINT="https://api.honeycomb.io"
# export OTEL_EXPORTER_OTLP_HEADERS="x-honeycomb-team=<ingest-key>"

store = OpenTelemetryStore()

openai_client = OpenAI(base_url="http://localhost:11434/v1", api_key="unused")

client = wrap_openai(openai_client, store=store)

response = client.chat.completions.create(
    model="llama3.1", messages=[{"role": "user", "content": "Tell me a joke."}]
)

# The OpenTelemetryStore links multiple completions into a trace
response = client.chat.completions.create(
    model="llama3.1", messages=[{"role": "user", "content": "Tell me another joke."}]
)
# Now query your Opentelemetry Compatible observability store as you usually do!
