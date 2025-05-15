from fastmcp import FastMCP
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
from dotenv import load_dotenv

# Load env vars
load_dotenv()

mcp = FastMCP("etl-agent")


@mcp.tool(name="etl_tool")
async def get_data_engineer_agent(question: str, csv_path: str = None) -> str:
    serverparams = StdioServerParameters(
        command="python",
        args=["my_mcp/etl_mcp_server.py"],
    )

    mcp_server_adapter = None

    try:
        mcp_server_adapter = MCPServerAdapter(serverparams)
        tools = mcp_server_adapter.tools
        llm = ChatOpenAI(model="gpt-4.1-mini")

        agent = Agent(
            role="Senior Data Engineer",
            goal=(
                "Automate end-to-end ETL pipelines: read, validate, clean, transform, and load data from CSV to Postgres. Always ensure best practices for data quality, robustness, and auditability."
            ),
            backstory=(
                "You are a senior data engineer with expertise in robust data pipelines. You can chain advanced ETL tools (MCP) and always follow best practices for data quality and governance."
            ),
            tools=tools,
            llm=llm,
            verbose=True,
        )

        task = Task(
            description=(
                f"You have access to the uploaded CSV file at: {csv_path}."
                f" Your task is: {question}"
                "Available tools include: reading data, checking data types, detecting anomalies, removing duplicates, handling missing values, standardizing values, enforcing constraints, and transforming data."
                "For tools that require specific parameters (e.g., rules, columns, strategies, type mappings), do NOT run the tool until you have all required details from the user."
                " If the user's request is missing necessary information (such as columns to process, anomaly rules, type mappings, or strategies), respond by asking the user exactly what is needed. Do not guess."
                "When you run a tool and it returns a changed table, always present the table to the user."
                " If the tool result is empty or unchanged (e.g. no duplicates found), just say 'No changes needed.'"
            ),
            expected_output="Return what you have found or done with the data.",
            tools=tools,
            agent=agent,
            verbose=True,
        )
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )
        result = await crew.kickoff_async()
        return result

    finally:
        if mcp_server_adapter:
            mcp_server_adapter.stop()


if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8000)
