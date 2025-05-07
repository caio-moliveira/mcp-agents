# app/client.py
from tools.mcp_tool import MCPServerAdapter
from server.supabase_server import get_supabase_server_params
from server.filesystem_server import get_filesystem_server_params
import logging

# Initialize logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_supabase_tools(extra_tools=None):
    try:
        logger.info("Loading Supabase tools...")
        params = get_supabase_server_params()
        mcp_adapter = MCPServerAdapter(params)
        tools = mcp_adapter.tools
        if extra_tools:
            tools += extra_tools
        logger.info("Supabase tools loaded successfully.")
        return tools
    except Exception:
        logger.error("Error loading Supabase tools:", exc_info=True)
        raise


def load_filesystem_tools(extra_tools=None):
    try:
        logger.info("Loading Filesystem tools...")
        params = get_filesystem_server_params()
        mcp_adapter = MCPServerAdapter(params)
        tools = mcp_adapter.tools
        if extra_tools:
            tools += extra_tools
        logger.info("Filesystem tools loaded successfully.")
        return tools
    except Exception:
        logger.error("Error loading Filesystem tools:", exc_info=True)
        raise
