import os

from huggingface_hub import AsyncInferenceClient

import observers

api_key = os.getenv("HF_TOKEN")


# Patch the HF client
hf_client = AsyncInferenceClient(token=api_key)
client = observers.wrap_hf_client(hf_client)


async def get_response() -> None:
    response = await client.chat.completions.create(
        model="Qwen/Qwen2.5-Coder-32B-Instruct",
        messages=[
            {
                "role": "user",
                "content": "Write a function in Python that checks if a string is a palindrome.",
            }
        ],
        stream=True,
    )

    async for chunk in response:
        print(chunk)


if __name__ == "__main__":
    import asyncio

    asyncio.run(get_response())
