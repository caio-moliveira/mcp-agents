from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from fastmcp import FastMCP
from crewai import Agent, Task, Crew
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

# Load env vars
load_dotenv()

mcp = FastMCP("AirbnbSearchServer")


@mcp.tool(name="search_airbnb")
def search_airbnb(question: str) -> str:
    """Search for Airbnb listings in a city with a max price per night."""

    llm = ChatOpenAI(model="gpt-4.1-mini")

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
    )

    with MCPServerAdapter(server_params) as tools:
        agent = Agent(
            role="Especialista em Busca do Airbnb",
            goal="Buscar e analisar informações de acomodações no Airbnb",
            backstory="Especialista em encontrar as melhores acomodações",
            tools=tools,
            llm=llm,
            verbose=True,
        )

        task = Task(
            description=f"Buscar informações de acomodações no Airbnb de acordo com {question}",
            expected_output="Lista de acomodações disponíveis com detalhes",
            agent=agent,
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True,
            llm=llm,
        )

        result = crew.kickoff()
        return result


if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8005)
