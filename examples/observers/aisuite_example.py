import aisuite as ai
from observers.observers import wrap_aisuite

client = ai.Client()

client = wrap_aisuite(client)

# ensure you have both `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` environment variables set
models = ["openai:gpt-4o", "anthropic:claude-3-5-sonnet-20240620"]

messages = [
    {"role": "system", "content": "Respond in Pirate English."},
    {"role": "user", "content": "Tell me a joke."},
]

for model in models:
    response = client.chat.completions.create(
        model=model, messages=messages, temperature=0.75
    )
    print(response.choices[0].message.content)
