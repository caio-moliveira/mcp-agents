from dotenv import load_dotenv
from fastmcp import FastMCP
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

# Load environment variables
load_dotenv()

# Instantiate the MCP server
mcp = FastMCP("selenium-agent-server")


@mcp.tool(name="selenium_scraper_tool")
async def selenium_scraper_tool(question: str) -> str:
    """Use Selenium MCP to scrape structured data from websites based on navigation instructions."""

    serverparams = StdioServerParameters(
        command="npx", args=["-y", "@angiejones/mcp-selenium"]
    )

    try:
        mcp_server_adapter = MCPServerAdapter(serverparams)
        tools = mcp_server_adapter.tools
        llm = ChatOpenAI(model="gpt-4.1-mini")

        # Agent focused on browser automation and scraping
        selenium_scraper_agent = Agent(
            role="Selenium Automation Analyst",
            goal=(
                "Scrape structured and unstructured data from websites using headless browser automation. "
                "Capable of navigating pages, extracting text, tables, images, and identifying dynamic elements."
            ),
            backstory=(
                "A browser automation expert trained in advanced scraping techniques using Selenium. "
                "Fluent in identifying DOM patterns, handling JavaScript-rendered content, and following detailed scraping instructions."
            ),
            tools=tools,
            verbose=True,
            llm=llm,
            allow_delegation=False,
        )

        # Task to execute the scraping workflow
        selenium_scraper_task = Task(
            description=(
                f"Follow these scraping instructions carefully: {question}. "
                "You must visit the site, extract the required elements, and return structured and clean results."
            ),
            expected_output=(
                "Extracted data formatted as clean text, tables, or JSON. "
                "Ensure content is accurate, relevant, and reflects what was requested in the instructions."
            ),
            tools=tools,
            agent=selenium_scraper_agent,
        )

        crew = Crew(
            agents=[selenium_scraper_agent],
            tasks=[selenium_scraper_task],
            process=Process.sequential,
            verbose=True,
        )

        result = await crew.kickoff_async()
        return result

    finally:
        mcp_server_adapter.stop()


# Run the MCP server
if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8003)
