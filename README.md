# MCP Test Suite

A professional, modular testbed for Model Context Protocol (MCP) servers and CrewAI-powered agents. This repository enables you to run, test, and interact with a variety of MCPs for data analysis, web search, financial analytics, database management, and more—all from a unified Python/Streamlit interface.

---

## Table of Contents
- [Repository Structure](#repository-structure)
- [Overview](#overview)
- [Supported MCP Servers](#supported-mcp-servers)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Running MCP Servers](#running-mcp-servers)
- [Streamlit Apps](#streamlit-apps)
- [Usage Examples](#usage-examples)
- [Contributing](#contributing)
- [License](#license)

---

## Repository Structure

- **src/**: Standalone MCP server modules (each file = one MCP server)
- **app/**: Streamlit apps
  - `multi_mcp_app.py`: Launches all MCP servers at once and lets the user select which LLM to use per query
  - `single_mcp_app.py`: Example of a single MCP/LLM chat app
- **llm/**: LLM provider definitions and utilities
- **project/**: Main project logic, including a multi-agent server that combines two MCPs in a single agent
- **example-env.env**: Example environment file showing required variables for `.env`
- **my_mcp/**: Contains your custom MCP server and related modules.
  - `etl_mcp_server.py`: Example MCP server implementation using FastMCP's `@mcp.tool` decorator to expose functions as tools.
  - `etl_agent.py`, `etl_app.py`, `test.py`: Additional logic, agent definitions, and tests for your custom server.

---

## Overview
This project demonstrates how to orchestrate and interact with multiple MCP servers using CrewAI agents. Each MCP server exposes a set of tools (APIs) for a specific domain, such as:
- Financial data (YFinance)
- Database analytics (Supabase)
- Web search (Brave Search)
- GitHub repository analysis
- Docker-based tool orchestration
- Documentation Q&A (Context7)
- Browser automation (Selenium)

You can run each MCP server independently, or use the provided Streamlit apps for a unified chat interface.

---

## Supported MCP Servers
Each server is implemented as a Python module in `src/`:

| Server                | File                          | Purpose                                      | Default Port |
|-----------------------|-------------------------------|----------------------------------------------|--------------|
| Supabase Analyst      | `src/supabase_mcp_server.py`  | SQL/CRUD on Supabase DB                      | 8000         |
| YFinance Analyst      | `src/yfinance_mcp_server.py`  | Financial data analytics                     | 8005         |
| Brave Web Search      | `src/brave_mcp_server.py`     | Web search and scraping                      | 8003         |
| GitHub Analyst        | `src/github_mcp_server.py`    | GitHub repo insights                         | 8001         |
| Docker MCP            | `src/docker_mcp_server.py`    | Run tools in Docker containers               | 8002         |
| Context7 Analyst      | `src/context7_mcp_server.py`  | Documentation/codebase Q&A                   | 8004         |
| Selenium Scraper      | `src/selenium_mcp_server.py`  | Browser automation and scraping              | 8003         |

**Multi-Agent Analyst:**
- `project/mcp_server.py`: Unified access to YFinance & Supabase in a single agent (port 8000)

---

## Quick Start

### 1. Clone the repository
```sh
git clone <your-repo-url>
cd mcp-test
```

### 2. Install dependencies (using [UV](https://github.com/astral-sh/uv))
```sh
uv pip install -r requirements.txt
# or, for editable mode:
uv pip install -e .
```

### 3. Set up environment variables
- Copy `example-env.env` to `.env`:
  ```sh
  cp example-env.env .env
  ```
- Fill in your API keys and tokens as shown in the example file.

---

## Configuration

- All sensitive credentials (API keys, tokens) are managed via the `.env` file.
- Required variables include:
  - `OPENAI_API_KEY`, `SUPABASE_ACCESS_TOKEN`, `BRAVE_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN`, etc.
- See `example-env.env` for a full list and format.

---

## Running MCP Servers

Each MCP server can be started individually. For example:

```sh
# Start Supabase MCP server
python src/supabase_mcp_server.py

# Start YFinance MCP server
python src/yfinance_mcp_server.py

# Start Brave Web Search MCP server
python src/brave_mcp_server.py

# Start Multi-Agent Analyst (unified)
python project/mcp_server.py
```

- By default, servers run on `localhost` with different ports (see table above).
- You can run multiple servers in parallel (in separate terminals).

---

## Streamlit Apps

Two Streamlit apps are provided for interactive chat with MCP agents:

- `app/multi_mcp_app.py`: Launches all MCP servers and lets you select the LLM and MCP for each query.
- `app/single_mcp_app.py`: Example of a single MCP/LLM chat app.

Run with:
```sh
streamlit run app/multi_mcp_app.py
# or
streamlit run app/single_mcp_app.py
```

---

## LLMs

- The `llm/` folder contains all available LLM provider definitions.
- You can select which LLM to use in the multi-agent Streamlit app.

---

## Usage Examples

- **Ask financial questions:**
  > "Show me the revenue growth of Apple over the last 5 years."
- **Query your Supabase DB:**
  > "List all users who signed up in the last month."
- **Analyze a GitHub repo:**
  > "Summarize the top contributors and open issues for repo X."
- **Perform web search:**
  > "Find the latest news about AI regulation."

All actions are performed securely via CrewAI-powered agents and MCP tools.

---

## Using MCP Servers with Desktop Claude

You can connect any MCP server from this repository to Desktop Claude for seamless local tool integration.

### 1. Start an MCP Server for Desktop Claude

Use the `fastmcp` CLI to launch the desired MCP server. For example, to run the YFinance MCP server:

```sh
fastmcp run src/yfinance_mcp_server.py:mcp
```

Replace `yfinance_mcp_server.py` with any other MCP server file in `src/` as needed.

### 2. Configure Desktop Claude

Edit your `claude_desktop_config.json` file to add the MCP server. Example configuration for YFinance:

```json
{
  "mcpServers": {
    "yfinance-agent-server": {
      "command": "<repository/path>/.venv/Scripts/python",
      "args": [
        "<repository/path>/src/yfinance_mcp_server.py"
      ]
    }
  }
}
```

- Replace `<repository/path>` with the absolute path to your local repository.
- Ensure the Python executable path matches your environment (e.g., `.venv/Scripts/python` on Windows).
- You can add multiple servers by duplicating the block under `mcpServers` and changing the server name and script.

After saving the config, restart Desktop Claude. The MCP server will be available as a local tool.

---

## Custom MCP Server: `my_mcp`

You can extend this test suite by adding your own MCP servers. This repository includes a sample custom MCP server in the `my_mcp/` directory. This is a great starting point for building and testing your own tools using the FastMCP framework.

### Structure
- **my_mcp/**: Contains your custom MCP server and related modules.
  - `etl_mcp_server.py`: Example MCP server implementation using FastMCP's `@mcp.tool` decorator to expose functions as tools.
  - `etl_agent.py`, `etl_app.py`, `test.py`: Additional logic, agent definitions, and tests for your custom server.

### How to Use Your Custom MCP Server

To use your custom MCP server and integrate it as a tool in your own Streamlit application, follow these steps:

1. **Start the Custom MCP Server**
   
   This launches the FastMCP server that exposes your ETL functions as tools:
   ```sh
   python my_mcp/etl_mcp_server.py
   ```

2. **Start the Agent**
   
   This script connects to the running MCP server, wraps it in an agent, and exposes the agent as a tool:
   ```sh
   python my_mcp/etl_agent.py
   ```

3. **Launch the Streamlit Application**
   
   This app uses the agent (now a tool) to provide an interactive UI for your ETL workflows:
   ```sh
   streamlit run my_mcp/etl_app.py
   ```

**Summary:**
- The MCP server (`etl_mcp_server.py`) exposes your functions as tools.
- The agent (`etl_agent.py`) connects to the MCP server and turns the agent into a tool for your app.
- The Streamlit app (`etl_app.py`) provides a user interface to interact with your agent/tool.

You can further customize each step to fit your workflow and add more tools or agents as needed.

---

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements, bug fixes, or new MCP integrations.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
