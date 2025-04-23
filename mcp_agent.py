# basic_mcp_agent.py

import asyncio
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from app.agent import build_agent


async def main():
    print("=== Pydantic AI MCP CLI Chat ===")
    print("Type 'exit' to quit the chat.\n")

    # Load and initialize the MCP agent and tools
    client, agent = await build_agent()
    messages = []
    console = Console()

    try:
        while True:
            user_input = input("[You] ")

            if user_input.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break

            try:
                print("[Assistant]")
                with Live("", console=console, vertical_overflow="visible") as live:
                    async with agent.run_stream(
                        user_input, message_history=messages
                    ) as result:
                        output = ""
                        async for chunk in result.stream_text(delta=True):
                            output += chunk
                            live.update(Markdown(output))

                        messages.extend(result.all_messages())

            except Exception as e:
                print(f"[Error] {e}")

    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
