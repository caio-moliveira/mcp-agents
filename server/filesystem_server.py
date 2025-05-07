# filesystem_mcp_server.py
import os
from dotenv import load_dotenv
import logging
from mcp import StdioServerParameters

# Initialize logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def get_filesystem_server_params():
    try:
        logger.info("Loading Filesystem MCP server parameters...")
        data_dir = os.getenv(
            "MCP_FILESYSTEM_DATA_DIR", "D:\\workspace\\github\\mcp-project\\data"
        )

        logger.info(f"Using data directory: {data_dir}")
        return StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "D:\\workspace\\github\\mcp-project\\data",
            ],
        )

    except Exception:
        logger.error("Error loading Filesystem MCP server parameters:", exc_info=True)
        raise


if __name__ == "__main__":
    params = get_filesystem_server_params()
    print("Starting Filesystem MCP server...")
    params.run()
