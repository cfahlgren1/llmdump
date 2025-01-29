from openai import OpenAI

from observers import wrap_openai


openai_client = OpenAI()

client = wrap_openai(openai_client)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Tell me a joke."}],
)
print(response)
