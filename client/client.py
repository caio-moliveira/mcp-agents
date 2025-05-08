from crewai_tools import MCPServerAdapter
from server.supabase_server import get_supabase_server_params
from server.filesystem_server import get_filesystem_server_params
import logging

# Initialize logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_filesystem_tools():
    """Load tools from the Filesystem MCP server."""
    try:
        logger.info("Initializing Filesystem MCP server...")

        # Initialize Filesystem MCP server
        filesystem_params = get_filesystem_server_params()
        with MCPServerAdapter(filesystem_params) as filesystem_tools:
            logger.info("Filesystem tools loaded successfully.")
            return filesystem_tools

    except Exception as e:
        logger.error("Error loading Filesystem tools:", exc_info=True)
        raise RuntimeError("Failed to load Filesystem tools") from e


def load_supabase_tools():
    """Load tools from the Supabase MCP server."""
    try:
        logger.info("Initializing Supabase MCP server...")

        # Initialize Supabase MCP server
        supabase_params = get_supabase_server_params()
        with MCPServerAdapter(supabase_params) as supabase_tools:
            logger.info("Supabase tools loaded successfully.")
            return supabase_tools

    except Exception as e:
        logger.error("Error loading Supabase tools:", exc_info=True)
        raise RuntimeError("Failed to load Supabase tools") from e
