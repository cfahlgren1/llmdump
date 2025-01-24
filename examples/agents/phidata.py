from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from observers.observers import wrap_openai
from openai import OpenAI


client = wrap_openai(OpenAI())

web_agent = Agent(
    name="Web Agent",
    model=OpenAIChat(id="gpt-4o", client=client),
    tools=[DuckDuckGo()],
    instructions=["Always include sources"],
    show_tool_calls=True,
    markdown=True,
)
web_agent.print_response("Whats happening in France?")
