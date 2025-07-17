from agentic.tools import IMAPTool
from agentic.common import Agent, AgentRunner
from agentic.models import GPT_4O_MINI
# This is the "hello world" agent example. A simple agent with a tool for getting weather reports.

MODEL=GPT_4O_MINI # try locally with LMSTUDIO_QWEN

agent = Agent(
    name="Email Agent",
    welcome="I am a simple agent here to help answer your email questions.",
    instructions="You are a helpful assistant that can access your email.",
    model=MODEL,
    tools=[IMAPTool()]
)

if __name__ == "__main__":
    AgentRunner(agent).repl_loop()
