from dotenv import load_dotenv
from fastmcp import FastMCP
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

load_dotenv()

# This file doesn't define tools — it consumes the scraper MCP server
mcp = FastMCP("scraper-agent-server")


@mcp.tool(name="scraper_tool")
async def analyze_price_page(url: str) -> str:
    """Use a CrewAI agent to analyze a product page using the MCP scraper tool."""
    # Connect to the local MCP scraper server
    serverparams = StdioServerParameters(
        command="python",
        args=["scraper_server.py"],  # Adjust path if needed
    )

    try:
        mcp_server_adapter = MCPServerAdapter(serverparams)
        tools = mcp_server_adapter.tools
        llm = ChatOpenAI(model="gpt-4.1-mini")

        # Define CrewAI agent
        analyst = Agent(
            role="Market Research Analyst",
            goal="Understand product pricing from web data using the scraper tool",
            backstory=(
                "An expert at gathering and interpreting product pricing data for competitive analysis. "
                "Uses tools to extract structured data from product pages and explain trends."
            ),
            tools=tools,
            llm=llm,
            verbose=True,
        )

        # Define the task using the `check_price` tool
        task = Task(
            description=f"Scrape and analyze product pricing for the page: {url}",
            expected_output="A structured summary of the product's name and price details",
            tools=tools,
            agent=analyst,
        )

        crew = Crew(
            agents=[analyst],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )

        result = await crew.kickoff_async()
        return result

    finally:
        mcp_server_adapter.stop()


if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8000)
