import os

from litellm import completion
from observers.observers.models.litellm import wrap_litellm

# ensure you have both `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` environment variables set
os.environ["OPENAI_API_KEY"] = "your-api-key"
os.environ["ANTHROPIC_API_KEY"] = "your-api-key"

completion = wrap_litellm(completion)

models = ["gpt-3.5-turbo", "claude-3-5-sonnet-20240620"]
messages = [{"content": "Hello, how are you?", "role": "user"}]

for model in models:
    response = completion(model=model, messages=messages, temperature=0.75)
    print(response.choices[0].message.content)
