# Travel MCP Agent

This project provides an AI-powered travel planner that connects three specialized agents—Flights, Accommodation, and Local Experiences—each running on its own MCP (Model Context Protocol) server. The agents collaborate to deliver a complete travel plan based on your preferences.

## Features
- **Flight Specialist Agent**: Finds relevant and affordable flights using real-time search tools.
- **Accommodation Finder Agent**: Recommends top-rated hotels, apartments, or hostels from Airbnb and similar sources.
- **Local Experience Curator Agent**: Suggests attractions, restaurants, and events tailored to your interests using web search.

## How It Works
- The main entry point is `app.py`, a Streamlit app for user interaction.
- The core logic is in `mcp_server.py`, which defines the three agents and connects them to their respective MCP servers:
  - **Flights**: Uses a Serper-based MCP server for flight search.
  - **Accommodation**: Uses an Airbnb MCP server for lodging options.
  - **Experiences**: Uses a Brave Search MCP server for local highlights.
- The agents are orchestrated using CrewAI, running in sequence to build a full travel plan.

## Usage
1. **Start the MCP server**
   ```powershell
   python travel_mcp_agent/mcp_server.py
   ```
   This launches the FastMCP server on `localhost:8003`.

2. **Run the Streamlit app**
   ```powershell
   streamlit run travel_mcp_agent/app.py
   ```
   Fill in your travel details and let the agents plan your trip!

## Customization
- Edit `schemas.py` to adjust the input fields.
- Modify `mcp_server.py` to add or change agent logic, tools, or LLMs.

## Requirements
- Python 3.10+
- All dependencies listed in the main `requirements.txt`
- API keys for Serper, Brave Search, and (optionally) Airbnb, set in your `.env` file

## Folder Contents
- `app.py`: Streamlit UI for travel planning
- `mcp_server.py`: Defines and runs the three-agent MCP server
- `schemas.py`: Input schema for travel planning

---
This module is part of the main MCP test suite and demonstrates multi-agent orchestration for real-world travel planning.
