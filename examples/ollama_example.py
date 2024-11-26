from observers.observers.models.openai import wrap_openai
from observers.stores.duckdb import DuckDBStore
from openai import OpenAI

store = DuckDBStore()

# Ollama is running locally at http://localhost:11434/v1
openai_client = OpenAI(
    base_url="http://localhost:11434/v1",
    # The openai client needs an api key to instantiate, but we
    # are using this to access ollama, which does not use it
    api_key='unused'
)

client = wrap_openai(openai_client, store=store)

response = client.chat.completions.create(
    model="llama3.1",
    messages=[{"role": "user", "content": "Tell me a joke."}],
)
