from fastmcp import FastMCP
from filesystem_server import get_filesystem_server_params
from supabase_server import get_supabase_server_params

# Initialize FastMCP server
mcp = FastMCP("MCP Server for Filesystem and Supabase")

# Initialize servers
filesystem_server = get_filesystem_server_params()
supabase_server = get_supabase_server_params()


# Register FilesystemServer as a tool
@mcp.tool(
    name="filesystem_tool",
    description="Tool for interacting with the filesystem server.",
)
def filesystem_tool(action: str, path: str) -> str:
    """Interact with the filesystem server."""
    return filesystem_server.run({"action": action, "path": path})


# Register SupabaseServer as a tool
@mcp.tool(
    name="supabase_tool", description="Tool for interacting with the Supabase server."
)
def supabase_tool(query: str, table: str) -> str:
    """Interact with the Supabase server."""
    return supabase_server.run({"query": query, "table": table})


if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run()
