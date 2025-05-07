# app/client.py
from mcp_tool import MCPServerAdapter
from server import get_supabase_server_params


def load_supabase_tools(extra_tools=None):
    params = get_supabase_server_params()
    mcp_adapter = MCPServerAdapter(params)
    tools = mcp_adapter.tools
    if extra_tools:
        tools += extra_tools
    return tools
