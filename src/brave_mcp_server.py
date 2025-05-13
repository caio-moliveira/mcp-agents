from dotenv import load_dotenv
from fastmcp import FastMCP
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
import os

# Load env vars
load_dotenv()

# Instantiate MCP server
mcp = FastMCP("brave-web-agent-server")


@mcp.tool(name="brave_web_search")
async def brave_web_search_tool(question: str) -> str:
    """Search the web and scrape relevant content using Brave Search MCP and a CrewAI-powered agent."""

    # MCP adapter is already configured for brave search (do not change)
    serverparams = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-brave-search"],
        env={"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY"), **os.environ},
    )

    try:
        mcp_server_adapter = MCPServerAdapter(serverparams)
        tools = mcp_server_adapter.tools
        llm = ChatOpenAI(model="gpt-4.1-mini")

        # Define Brave Web Search Agent
        brave_search_agent = Agent(
            role="Web Intelligence Analyst",
            goal=(
                "Expertly perform real-time web searches and scrape relevant, trustworthy information "
                "from online sources using Brave Search and MCP tools. Synthesize results into useful, actionable responses."
            ),
            backstory=(
                "A highly capable agent skilled in navigating and extracting knowledge from live webpages. "
                "Specializes in identifying authoritative sources, summarizing content accurately, and retrieving useful data "
                "from news sites, blogs, developer forums, and technical documentation via Brave Search."
            ),
            tools=tools,
            verbose=True,
            llm=llm,
            allow_delegation=False,
        )

        # Define the search task
        brave_search_task = Task(
            description=f"Conduct a precise and reliable web search to answer this query: {question}",
            expected_output=(
                "A high-quality summary, list of insights, or direct answers from credible web sources. "
                "The result should show critical thinking in parsing web data and deliver practical, clear, and accurate information."
            ),
            tools=tools,
            agent=brave_search_agent,
        )

        crew = Crew(
            agents=[brave_search_agent],
            tasks=[brave_search_task],
            process=Process.sequential,
            verbose=True,
        )

        result = await crew.kickoff_async()
        return result

    finally:
        mcp_server_adapter.stop()


if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8003)
