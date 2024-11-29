from observers.observers import wrap_openai
from openai import OpenAI

# Ollama is running locally at http://localhost:11434/v1
openai_client = OpenAI(base_url="http://localhost:11434/v1")

client = wrap_openai(openai_client)

response = client.chat.completions.create(
    model="llama3.1", messages=[{"role": "user", "content": "Tell me a joke."}]
)
