# app/client.py
from app.mcp_tool import MCPServerAdapter
from app.server import get_supabase_server_params


def load_supabase_tools(extra_tools=None):
    params = get_supabase_server_params()
    mcp_adapter = MCPServerAdapter(params)
    tools = mcp_adapter.tools
    if extra_tools:
        tools += extra_tools
    return tools
