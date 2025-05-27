# mcp_server.py

from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from langchain_openai import ChatOpenAI
from schemas import TravelInput
import agentops

load_dotenv()

mcp = FastMCP("agent-server")

AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")
agentops.init(AGENTOPS_API_KEY, default_tags=["travel_planner"])


@mcp.tool(name="travel_planner")
def run_travel_planner(input_data: TravelInput):
    flights_params = StdioServerParameters(
        command="npx",
        args=["-y", "serper-search-scrape-mcp-server"],
        env={"SERPER_API_KEY": os.getenv("SERPER_API_KEY"), **os.environ},
    )
    airbnb_params = StdioServerParameters(
        command="npx",
        args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
        env=os.environ,
    )
    bravesearch_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-brave-search"],
        env={"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY"), **os.environ},
    )

    bravesearch_llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    flights_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
    airbnb_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    backup_llm = LLM(
        model="ollama/llama3.3:latest",
        base_url="http://localhost:11434",
        temperature=0.1,
    )
    with (
        MCPServerAdapter(flights_params) as flights_tools,
        MCPServerAdapter(airbnb_params) as airbnb_tools,
        MCPServerAdapter(bravesearch_params) as bravesearch_tools,
    ):
        flights_agent = Agent(
            role="Flight Specialist Agent",
            goal="Provide the most relevant and affordable flight options based on user travel preferences.",
            backstory="An AI expert in global flight searches with access to major airlines and travel aggregators. "
            "Trained to optimize for best departure timing, price, and overall travel experience.",
            tools=flights_tools,
            llm=flights_llm,
            verbose=True,
        )

        airbnb_agent = Agent(
            role="Accommodation Finder Agent",
            goal="Identify the most suitable and top-rated accommodations that match user expectations and budget.",
            backstory="An AI agent with advanced knowledge of short-term rentals. Skilled at finding apartments, hotels, "
            "and boutique stays that align with user preferences like location, amenities, and ratings.",
            tools=airbnb_tools,
            llm=airbnb_llm,
            verbose=True,
        )

        bravesearch_agent = Agent(
            role="Local Experience Curator Agent",
            goal="Discover the most popular and enjoyable attractions, restaurants, and local events that align with user interests.",
            backstory="An AI guide deeply familiar with global destinations, local happenings, and top-rated venues. Skilled at curating experiences based on personal preferences such as food, culture, parks, and nightlife. Always focused on what’s happening during the user's visit.",
            tools=bravesearch_tools,
            llm=bravesearch_llm,
            verbose=True,
        )

        flights_task = Task(
            description=(
                f"Search for top-rated and cost-effective flights departing from {input_data.departure} to "
                f"{input_data.destination} on {input_data.start_date}. Filter results for {input_data.num_travelers} "
                f"passenger(s), and present options from trustworthy sources."
            ),
            expected_output=(
                "A concise list (max 5) of available flights with:\n"
                "- Airline name\n"
                "- Departure time and total duration\n"
                "- Price per traveler (approximate)\n"
                "- Booking link"
            ),
            agent=flights_agent,
        )

        airbnb_task = Task(
            description=(
                f"Search for available {input_data.accommodation_type} accommodations in {input_data.destination} from "
                f"{input_data.start_date} to {input_data.end_date} for {input_data.num_travelers} traveler(s). Prioritize "
                f"listings with high ratings, guest satisfaction, and fitting to general travel budgets."
            ),
            expected_output=(
                "A list of up to 5 recommended accommodations with:\n"
                "- Listing name\n"
                "- Total price and price per night\n"
                "- Rating (and number of reviews)\n"
                "- Key features (e.g., host type, free cancellation)\n"
                "- Direct booking link"
            ),
            agent=airbnb_agent,
        )

        bravesearch_task = Task(
            description=(
                f"Search for attractions, events, and local highlights in {input_data.destination} "
                f"from {input_data.start_date} to {input_data.end_date} that align with the user's interests: "
                f"{', '.join(input_data.attractions)}. Include must-visit places, famous restaurants, parks, nightlife, or "
                f"festivals occurring during the travel dates."
            ),
            expected_output=(
                "A curated list of up to 5 recommendations including:\n"
                "- Name of the place or event\n"
                "- What it is and why it’s recommended\n"
                "- Address or neighborhood\n"
                "- Opening dates/times if applicable\n"
                "- Website or source link for more details"
            ),
            agent=bravesearch_agent,
        )

        crew = Crew(
            agents=[flights_agent, airbnb_agent, bravesearch_agent],
            tasks=[flights_task, airbnb_task, bravesearch_task],
            process=Process.sequential,
            verbose=True,
            llm=backup_llm,
            max_iterations=3,
        )

        return crew.kickoff()


if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8003)
