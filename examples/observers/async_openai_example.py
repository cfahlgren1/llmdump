import asyncio
import os

from openai import AsyncOpenAI

from observers import wrap_openai

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

client = wrap_openai(openai_client)


async def get_response() -> None:
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Tell me a joke."}],
    )
    print(response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(get_response())
