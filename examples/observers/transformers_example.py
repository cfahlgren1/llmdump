import os

from httpx import stream

import observers
from transformers import pipeline


token = os.getenv("HF_TOKEN")
pipe = pipeline(
    "text-generation",
    model="Qwen/Qwen2.5-0.5B-Instruct",
    token=token,
    Stream()
)
client = observers.wrap_transformers(pipe)
messages = [
    {
        "role": "system",
        "content": "You are a pirate chatbot who always responds in pirate speak!",
    },
    {"role": "user", "content": "Who are you?"},
]
response = client.chat.completions.create(
    messages=messages,
    max_new_tokens=256,
)
print(response)
