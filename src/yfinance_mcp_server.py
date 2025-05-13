from dotenv import load_dotenv
from fastmcp import FastMCP
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

# Load env vars
load_dotenv()

# Instantiate MCP server
mcp = FastMCP("yfinance-agent-server")


@mcp.tool(name="yfinance_analyst")
async def yfinance_analyst_tool(question: str) -> str:
    """Analyze yfinance library and answer questions about out data using CrewAI-powered agent."""
    # Set up MCPServerAdapter to talk to the Supabase stock tools server

    serverparams = StdioServerParameters(
        command="uvx",
        args=["yfmcp@latest"],
    )

    try:
        mcp_server_adapter = MCPServerAdapter(serverparams)
        tools = mcp_server_adapter.tools
        llm = ChatOpenAI(model="gpt-4.1-mini")

        # Define CrewAI agent
        finance_analyst = Agent(
            role="Senior Finance Analyst",
            goal=(
                "Analyze, interpret, and respond to any financial data request using expert-level knowledge "
                "of corporate finance, accounting, market data, and SQL. Provide clear insights and accurate data analysis."
            ),
            backstory=(
                "A highly experienced financial analyst with a strong background in corporate finance, market research, and data analytics. "
                "Trained to understand complex financial statements, investment metrics, and economic indicators, and to convert user requests "
                "into precise SQL queries or structured financial insights. Has deep knowledge of stock markets, financial KPIs, company performance, "
                "and can advise users on revenue, profit trends, valuation ratios, and much more. Adept at interpreting business objectives and "
                "retrieving or transforming the right data from financial databases."
            ),
            tools=tools,
            verbose=True,
            llm=llm,
            allow_delegation=False,
        )

        # Define task
        finance_task = Task(
            description=f"Answer this financial data request accurately: {question}",
            expected_output="A concise, accurate SQL query result or an explanation of the financial insight retrieved.",
            tools=tools,
            agent=finance_analyst,
        )

        crew = Crew(
            agents=[finance_analyst],
            tasks=[finance_task],
            process=Process.sequential,
            verbose=True,
        )

        result = await crew.kickoff_async()
        return result

    finally:
        mcp_server_adapter.stop()


if __name__ == "__main__":
    # mcp.run(transport="sse", host="127.0.0.1", port=8005)
    # mcp.run(transport="stdio")
    import asyncio
    import os

    port = os.environ.get("PORT", 8888)

    asyncio.run(
        mcp.run_sse_async(
            host="0.0.0.0",
            port=8888,
            log_level="debug",
        )
    )
