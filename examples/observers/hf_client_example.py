import os

from huggingface_hub import InferenceClient

import observers

api_key = os.environ["HF_TOKEN"]

# Patch the HF client
hf_client = InferenceClient(token=api_key)
client = observers.wrap_hf_client(hf_client)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-Coder-32B-Instruct",
    messages=[{"role": "user", "content": "Tell me a joke."}],
)
