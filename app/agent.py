# app/agent.py
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from app import config
from app.mcp_client import MCPClient


def get_model():
    return OpenAIModel(config.MODEL_CHOICE)


def deduplicate_tools(tools):
    seen, unique = set(), []
    for tool in tools:
        if tool.name not in seen:
            seen.add(tool.name)
            unique.append(tool)
    return unique


async def build_agent():
    client = MCPClient()
    client.load_servers(str(config.CONFIG_FILE))
    tools = await client.start()
    unique_tools = deduplicate_tools(tools)
    return client, Agent(model=get_model(), tools=unique_tools)
