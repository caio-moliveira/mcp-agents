# app/config.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "mcp_config.json"

# Access secrets from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_CHOICE = os.getenv("MODEL_CHOICE", "gpt-4o-mini")
