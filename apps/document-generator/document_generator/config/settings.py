"""
Configuration and environment-based settings for Document Generator.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env in current directory if present
env_path = Path(__file__).parents[2] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

class Settings:
    """Load settings from environment variables."""
    def __init__(self):
        # Default model
        self.model_name = os.environ.get("MODEL_NAME", "gpt-4")
        # API key
        self.api_key = os.environ.get("API_KEY", "")