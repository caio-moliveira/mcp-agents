from dotenv import load_dotenv
from fastmcp import FastMCP
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

# Load env vars
load_dotenv()

# Instantiate MCP server
mcp = FastMCP("context7-agent-server")


@mcp.tool(name="context7_analyst")
async def context7_analyst_tool(question: str) -> str:
    """Analyze context7 to retrieve any information about any documentation using CrewAI-powered agent."""
    # Set up MCPServerAdapter to talk to the context7 MCP server
    serverparams = StdioServerParameters(
        command="npx",
        args=["-y", "@upstash/context7-mcp@latest"],
    )

    try:
        mcp_server_adapter = MCPServerAdapter(serverparams)
        tools = mcp_server_adapter.tools
        llm = ChatOpenAI(model="gpt-4.1-mini")

        # Define CrewAI agent
        context7_analyst = Agent(
            role="Elite Documentation Intelligence Analyst",
            goal=(
                "Expertly interpret and extract information from complex technical documentation, codebases, and APIs using MCP context7. "
                "Turn vague or complex questions into accurate and actionable insights by querying documentation efficiently."
            ),
            backstory=(
                "An elite-level AI agent trained in deep comprehension of software libraries, technical APIs, and financial codebases. "
                "Built to understand natural language queries and translate them into focused searches against context-rich documentation systems like context7. "
                "Capable of analyzing results and providing clear explanations, code snippets, usage examples, and architectural insights. "
                "Operates with precision and domain-adaptability, making it ideal for developers, analysts, or business users seeking clarity on any documented system."
            ),
            tools=tools,
            verbose=True,
            llm=llm,
            allow_delegation=False,
        )

        # Define task
        context7_task = Task(
            description=f"Interpret and respond to this documentation query with technical accuracy: {question}",
            expected_output=(
                "A detailed yet clear explanation, code example, or configuration snippet based on context7 search. "
                "The response should be technically correct, concise, and directly solve the user's intent or clarify the documentation topic in question."
            ),
            tools=tools,
            agent=context7_analyst,
        )

        crew = Crew(
            agents=[context7_analyst],
            tasks=[context7_task],
            process=Process.sequential,
            verbose=True,
        )

        result = await crew.kickoff_async()
        return result

    finally:
        mcp_server_adapter.stop()


if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8004)
