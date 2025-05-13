from dotenv import load_dotenv
from fastmcp import FastMCP
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
import os
from mcp import StdioServerParameters

# Load env vars
load_dotenv()

# Instantiate MCP server
mcp = FastMCP("supabase-agent-server")


@mcp.tool(name="supabase_analyst")
async def supabase_analyst_tool(question: str) -> str:
    """Analyze supabase tables and answer questions about out data using CrewAI-powered agent."""
    # Set up MCPServerAdapter to talk to the Supabase stock tools server

    serverparams = StdioServerParameters(
        command="npx",
        args=["-y", "@supabase/mcp-server-supabase@latest"],
        env={"SUPABASE_ACCESS_TOKEN": os.getenv("SUPABASE_ACCESS_TOKEN"), **os.environ},
    )

    try:
        mcp_server_adapter = MCPServerAdapter(serverparams)
        tools = mcp_server_adapter.tools
        llm = ChatOpenAI(model="gpt-4.1-mini")

        # Define CrewAI agent
        analyst = Agent(
            role="Data Analyst",
            goal="Interpret and execute data-related instructions using SQL",
            backstory=(
                "An expert in data analysis and SQL who can understand business needs and convert "
                "them into SQL queries to interact with the database."
            ),
            tools=tools,
            verbose=True,
            llm=llm,
            allow_delegation=False,
        )

        # Define task
        task = Task(
            description=f"Execute the following data request: {question}",
            expected_output="SQL query result or confirmation of action taken",
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
