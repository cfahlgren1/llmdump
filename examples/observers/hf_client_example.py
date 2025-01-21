import asyncio

from huggingface_hub import AsyncInferenceClient

import observers

# api_key = os.getenv("HF_TOKEN")

hf_client = AsyncInferenceClient()
client = observers.wrap_hf_client(hf_client)


async def main():
    # Patch the HF client
    response = await client.chat.completions.create(
        model="Qwen/Qwen2.5-Coder-32B-Instruct",
        messages=[
            {
                "role": "user",
                "content": "Write a function in Python that checks if a string is a palindrome.",
            }
        ],
        max_tokens=10,
        stream=True,
    )

    async for chunk in response:
        print(chunk)


if __name__ == "__main__":
    asyncio.run(main())
