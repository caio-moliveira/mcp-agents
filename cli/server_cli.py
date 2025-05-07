from mcp.server.fastmcp import FastMCP
from client.client import load_supabase_tools
import logging

# Initialize logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

mcp = FastMCP("Supabase Agent Tools")

tools = load_supabase_tools()

# Wrap each CrewAIMCPTool as a FastMCP-compatible function
for tool in tools:
    try:
        logger.info(f"Registering tool: {tool.name}")

        def make_wrapper(tool_obj):
            def wrapper(**kwargs):
                return tool_obj.run(kwargs)

            wrapper.__name__ = tool.name  # required by FastMCP
            return wrapper

        wrapped_fn = make_wrapper(tool)
        mcp.add_tool(wrapped_fn, name=tool.name, description=tool.description)
        logger.info(f"Tool registered successfully: {tool.name}")
    except Exception as e:
        logger.error(f"Error registering tool {tool.name}: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    mcp.run()
