from dotenv import load_dotenv
from fastmcp import FastMCP
from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
import os
from llm.llms import gpt_4_1_mini

# Load environment variables from .env (if you have any)
load_dotenv()

# Instantiate a FastMCP server named "docker-agent-server"
mcp = FastMCP("docker-agent-server")


@mcp.tool(name="docker_mcp_tool")
async def docker_mcp_tool(question: str) -> str:
    """
    Proxy a user question into your Docker-based MCP server via CrewAI.
    """

    # We're going to run the MCP server inside Docker (via UVX)
    serverparams = StdioServerParameters(
        command="uvx",
        args=[
            "mcp-server-docker",
        ],
        env={**os.environ},
    )

    try:
        # Spin up the MCP adapter over stdio
        mcp_server_adapter = MCPServerAdapter(serverparams)
        tools = mcp_server_adapter.tools

        # Choose your LLM for CrewAI
        llm = gpt_4_1_mini()

        # Define a CrewAI agent that uses the Docker MCP tools
        docker_analyst = Agent(
            role="Docker MCP Intelligence Analyst",
            goal=(
                "Use the Docker-hosted MCP server to run tools and return structured "
                "answers for arbitrary user questions."
            ),
            backstory=(
                "You are an AI analyst interfacing with a Docker-deployed MCP server. "
                "When given a natural-language question, you should select and invoke "
                "the appropriate MCP tool, then summarize the output."
            ),
            tools=tools,
            verbose=True,
            llm=llm,
            allow_delegation=False,
        )

        # Wrap the user question into a single Task
        docker_task = Task(
            description=f"Answer this question using Docker MCP tools: {question}",
            expected_output=(
                "A concise, evidence-based answer, potentially including JSON or tabular data "
                "as returned by the MCP server tools."
            ),
            tools=tools,
            agent=docker_analyst,
        )

        # Run it all
        crew = Crew(
            agents=[docker_analyst],
            tasks=[docker_task],
            process=Process.sequential,
            verbose=True,
        )

        result = await crew.kickoff_async()
        return result

    finally:
        mcp_server_adapter.stop()


if __name__ == "__main__":
    # Expose via SSE on localhost:8000
    mcp.run(transport="sse", host="127.0.0.1", port=8002)
