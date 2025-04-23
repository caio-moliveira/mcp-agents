# app/mcp_server.py

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="Custom Tool Server",
    host="0.0.0.0",
    port=8050,
)


@mcp.tool()
def ping() -> str:
    """Simple tool to verify the MCP server is alive."""
    return "MCP server is running and responsive."


if __name__ == "__main__":
    mcp.run(transport="stdio")
