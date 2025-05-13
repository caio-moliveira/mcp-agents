import streamlit as st
import asyncio
from fastmcp import Client
import json
import pandas as pd
import importlib.util
import sys
from pathlib import Path

st.set_page_config(page_title="Supabase Analyst Chat", page_icon="📊", layout="wide")
st.title("Supabase Analyst – AI Chat Interface")

st.markdown("""
This professional interface allows you to chat with an AI agent to analyze and manage your Supabase database. You can:
- Ask questions about your tables and data
- Retrieve information
- Perform any CRUD (Create, Read, Update, Delete) operations

**All actions are performed securely via the CrewAI-powered agent.**
""")

# --- LLM and MCP Agent Selection ---
# Dynamically import llms.py
llms_path = Path(__file__).parent.parent / "llm" / "llms.py"
spec = importlib.util.spec_from_file_location("llms", str(llms_path))
llms = importlib.util.module_from_spec(spec)
sys.modules["llms"] = llms
spec.loader.exec_module(llms)

# List available LLMs (function names ending with _llama, _groq, _mini, _nano, _flash, etc.)
llm_options = [
    f
    for f in dir(llms)
    if callable(getattr(llms, f))
    and not f.startswith("_")
    and f not in ["get_openai_llm", "get_groq_llm", "get_ollama_llm", "get_gemini_llm"]
]
llm_options.sort()

# List available MCP agents/servers (from the server files)
mcp_agents = [
    ("Supabase Analyst", "supabase_analyst", "http://127.0.0.1:8000/sse"),
    ("GitHub Analyst", "github_analyst", "http://127.0.0.1:8001/sse"),
    ("Docker Analyst", "docker_mcp_tool", "http://127.0.0.1:8002/sse"),
    ("Brave Web Search", "brave_web_search", "http://127.0.0.1:8003/sse"),
    ("Context7 Analyst", "context7_analyst", "http://127.0.0.1:8004/sse"),
    ("YFinance Analyst", "yfinance_analyst", "http://127.0.0.1:8005/sse"),
]

# UI for LLM and MCP agent selection
st.sidebar.header("Configuration")
selected_llm = st.sidebar.selectbox("Select LLM", llm_options, index=0)
selected_agent = st.sidebar.selectbox(
    "Select MCP Agent", [a[0] for a in mcp_agents], index=0
)

# Get agent/tool name and server URL
agent_tool, agent_url = None, None
for name, tool, url in mcp_agents:
    if name == selected_agent:
        agent_tool = tool
        agent_url = url
        break

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Helper: Call the MCP agent server via SSE, passing LLM info if needed
async def call_agent(question: str, llm_name: str, agent_tool: str, agent_url: str):
    client = Client(agent_url)
    async with client:
        # Optionally, pass llm_name to the backend if supported
        params = {"question": question, "llm": llm_name}
        try:
            result = await client.call_tool(agent_tool, params)
        except Exception:
            # Fallback: try without llm param if not supported
            result = await client.call_tool(agent_tool, {"question": question})
        return result[0].text if result and hasattr(result[0], "text") else str(result)


# Accept user input
if prompt := st.chat_input("Ask me anything ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("The agent is thinking..."):
            try:
                response = asyncio.run(
                    call_agent(prompt, selected_llm, agent_tool, agent_url)
                )
                # Try to pretty print JSON or show as DataFrame if possible
                # If the response is a JSON object with 'raw' and 'tasks_output', extract the most relevant 'raw'
                try:
                    resp_json = json.loads(response)
                    # If response is a dict with 'raw' and 'tasks_output', prefer tasks_output[0]['raw'] if present
                    if isinstance(resp_json, dict):
                        if (
                            "tasks_output" in resp_json
                            and isinstance(resp_json["tasks_output"], list)
                            and len(resp_json["tasks_output"]) > 0
                            and "raw" in resp_json["tasks_output"][0]
                        ):
                            display_data = resp_json["tasks_output"][0]["raw"]
                        elif "raw" in resp_json:
                            display_data = resp_json["raw"]
                        else:
                            display_data = response
                    else:
                        display_data = response
                except Exception:
                    display_data = response

                # Now try to display display_data as DataFrame or pretty JSON
                try:
                    data = json.loads(display_data)
                    if isinstance(data, list) and all(
                        isinstance(row, dict) for row in data
                    ):
                        df = pd.DataFrame(data)
                        st.dataframe(df)
                        response = None
                    else:
                        st.json(data)
                        response = None
                except Exception:
                    response = display_data
            except Exception as e:
                import traceback

                tb = traceback.format_exc()
                response = f"Error: {e}\n\nTraceback:\n{tb}"
            if response:
                st.markdown(response)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response if response else "[Structured output above]",
        }
    )
