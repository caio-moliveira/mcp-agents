# supabase_mcp_server.py
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


def get_supabase_server_params():
    try:
        logger.info("Loading Supabase server parameters...")
        access_token = os.getenv("SUPABASE_ACCESS_TOKEN")

        if not access_token:
            logger.error("SUPABASE_ACCESS_TOKEN is not defined in the .env file.")
            raise ValueError("SUPABASE_ACCESS_TOKEN is not defined in the .env file.")

        logger.info("Supabase server parameters loaded successfully.")
        return StdioServerParameters(
            command="npx",
            args=["-y", "@supabase/mcp-server-supabase@latest"],
            env={"SUPABASE_ACCESS_TOKEN": access_token, **os.environ},
        )
    except Exception as e:
        logger.error(f"Error loading Supabase server parameters: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    params = get_supabase_server_params()
    print("Starting Supabase MCP server...")
    params.run()
