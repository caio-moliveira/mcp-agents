from dotenv import load_dotenv
import pathlib
import asyncio
import sys
import os
from pydantic_ai import Agent
from openai import AsyncOpenAI, OpenAI
from pydantic_ai.models.openai import OpenAIModel
from rich.markdown import Markdown
from rich.console import Console
from rich.live import Live
import mcp_client

# Get the directory where the current script is located
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
# Define the path to the config file relative to the script directory
CONFIG_FILE = SCRIPT_DIR / "mcp_config.json"

load_dotenv()


def get_model():
    llm = os.getenv("MODEL_CHOICE", "gpt-4o-mini")

    return OpenAIModel(llm)


def deduplicate_tools(tools):
    seen = set()
    unique = []
    for tool in tools:
        if tool.name not in seen:
            seen.add(tool.name)
            unique.append(tool)
    return unique


async def get_pydantic_ai_agent():
    client = mcp_client.MCPClient()
    client.load_servers(str(CONFIG_FILE))
    tools = await client.start()
    unique_tools = deduplicate_tools(tools)
    return client, Agent(model=get_model(), tools=unique_tools)


async def main():
    print("=== Pydantic AI MCP CLI Chat ===")
    print("Type 'exit' to quit the chat")

    # Initialize the agent and message history
    mcp_client, mcp_agent = await get_pydantic_ai_agent()
    console = Console()
    messages = []

    try:
        while True:
            # Get user input
            user_input = input("\n[You] ")

            # Check if user wants to exit
            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                print("Goodbye!")
                break

            try:
                # Process the user input and output the response
                print("\n[Assistant]")
                with Live("", console=console, vertical_overflow="visible") as live:
                    async with mcp_agent.run_stream(
                        user_input, message_history=messages
                    ) as result:
                        curr_message = ""
                        async for message in result.stream_text(delta=True):
                            curr_message += message
                            live.update(Markdown(curr_message))

                    # Add the new messages to the chat history
                    messages.extend(result.all_messages())

            except Exception as e:
                print(f"\n[Error] An error occurred: {str(e)}")
    finally:
        # Ensure proper cleanup of MCP client resources when exiting
        await mcp_client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
