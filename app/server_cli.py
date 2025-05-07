from mcp.server.fastmcp import FastMCP
from client import load_supabase_tools

mcp = FastMCP("Supabase Agent Tools")

tools = load_supabase_tools()

# Wrap each CrewAIMCPTool as a FastMCP-compatible function
for tool in tools:

    def make_wrapper(tool_obj):
        def wrapper(**kwargs):
            return tool_obj.run(kwargs)

        wrapper.__name__ = tool.name  # required by FastMCP
        return wrapper

    wrapped_fn = make_wrapper(tool)
    mcp.add_tool(wrapped_fn, name=tool.name, description=tool.description)

if __name__ == "__main__":
    mcp.run()
