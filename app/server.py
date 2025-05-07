# supabase_mcp_server.py
import os
from dotenv import load_dotenv
from mcp import StdioServerParameters


def get_supabase_server_params():
    load_dotenv()
    access_token = os.getenv("SUPABASE_ACCESS_TOKEN")

    if not access_token:
        raise ValueError("A variável SUPABASE_ACCESS_TOKEN não está definida no .env.")

    return StdioServerParameters(
        command="npx",
        args=["-y", "@supabase/mcp-server-supabase@latest"],
        env={"SUPABASE_ACCESS_TOKEN": access_token, **os.environ},
    )


if __name__ == "__main__":
    params = get_supabase_server_params()
    print("Starting Supabase MCP server...")
    params.run()
