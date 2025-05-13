from dotenv import load_dotenv
from fastmcp import FastMCP
from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
import os
from llm.llms import deepseek_r1_8b_ollama

# Load env vars
load_dotenv()

# Instantiate MCP server
mcp = FastMCP("github-agent-server")


@mcp.tool(name="github_analyst")
async def github_analyst_tool(question: str) -> str:
    """Analyze github repositories data using CrewAI-powered agent."""

    serverparams = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={
            "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"),
            **os.environ,
        },
    )

    try:
        mcp_server_adapter = MCPServerAdapter(serverparams)
        tools = mcp_server_adapter.tools
        llm = deepseek_r1_8b_ollama()
        # llm = ChatOpenAI(model="gpt-4.1-mini")

        # Define CrewAI agent
        github_analyst = Agent(
            role="GitHub Intelligence Analyst",
            goal=(
                "Analyze GitHub repositories and provide intelligent insights on repository activity, contribution trends, issue tracking, "
                "and project health based on user questions."
            ),
            backstory=(
                "A technical AI analyst trained to deeply understand GitHub repository data — including commits, issues, PRs, contributors, code structure, "
                "and community health. Skilled in turning natural language questions into structured queries that retrieve and explain GitHub insights. "
                "Helps engineering teams, PMs, and CTOs understand the state and evolution of their codebases. Capable of summarizing repo metrics, "
                "detecting activity patterns, and providing evidence-backed interpretations from GitHub data sources."
            ),
            tools=tools,
            verbose=True,
            llm=llm,
            allow_delegation=False,
        )

        # Define task
        github_task = Task(
            description=f"Understand and answer the following GitHub-related question: {question}",
            expected_output=(
                "A clear, insightful answer to the user's question, supported by GitHub data. The response may include metrics, summaries of repo activity, "
                "lists of top contributors or open issues, and explanations of trends, depending on the nature of the query. "
                "If applicable, include repository names, relevant counts, and timeframes."
            ),
            tools=tools,
            agent=github_analyst,
        )

        crew = Crew(
            agents=[github_analyst],
            tasks=[github_task],
            process=Process.sequential,
            verbose=True,
        )

        result = await crew.kickoff_async()
        return result

    finally:
        mcp_server_adapter.stop()


if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8001)
