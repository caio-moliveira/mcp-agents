import streamlit as st
import asyncio
from fastmcp import Client
import json
import pandas as pd
import tempfile
import os

st.set_page_config(page_title="Data Engineer ETL Assistant", layout="centered")
st.title("Senior Data Engineer AI Assistant")

st.write("""
1. Upload a CSV file to explore and analyze it with our AI-powered ETL tools.
2. Ask anything about your data, or have the agent use any ETL tool on it.
""")

# Session state init
if "csv_path" not in st.session_state:
    st.session_state.csv_path = None
if "csv_data" not in st.session_state:
    st.session_state.csv_data = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# File upload widget
uploaded_file = st.file_uploader("Upload your CSV", type=["csv"], key="csv_upload")

# On upload, show as dataframe and store in session
if uploaded_file:
    # Read and display CSV immediately
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)
    st.session_state.csv_data = df.to_dict(orient="records")  # For AI agent context
    # Save to temp path for agent tools (if needed)
    temp_dir = tempfile.mkdtemp()
    temp_csv_path = os.path.join(temp_dir, uploaded_file.name)
    with open(temp_csv_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.session_state.csv_path = temp_csv_path

# If no new upload, but session already has CSV data, show it
elif st.session_state.csv_data:
    st.dataframe(pd.DataFrame(st.session_state.csv_data))

# ---- Display chat history ----
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Helper: Call the MCP agent server via SSE
async def call_agent(question: str, csv_path: str = None):
    client = Client("http://127.0.0.1:8001/sse")
    context = {"question": question}
    if csv_path:
        context["csv_path"] = csv_path
    async with client:
        result = await client.call_tool("etl_tool", context)
        return result[0].text if result and hasattr(result[0], "text") else str(result)


# ---- User Chat ----
if prompt := st.chat_input("Ask me anything about your uploaded data..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("The agent is thinking..."):
            try:
                response = asyncio.run(call_agent(prompt, st.session_state.csv_path))
                # Try to display as DataFrame or pretty JSON if agent returns tabular result
                try:
                    resp_json = json.loads(response)
                    if (
                        isinstance(resp_json, dict)
                        and "tasks_output" in resp_json
                        and isinstance(resp_json["tasks_output"], list)
                        and len(resp_json["tasks_output"]) > 0
                        and "raw" in resp_json["tasks_output"][0]
                    ):
                        display_data = resp_json["tasks_output"][0]["raw"]
                    elif "raw" in resp_json:
                        display_data = resp_json["raw"]
                    else:
                        display_data = response
                except Exception:
                    display_data = response

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
