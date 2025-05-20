"""Configuration settings for the Recipe Executor app."""

from typing import Any, Dict, List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the Recipe Executor app."""

    # App settings
    app_title: str = "Recipe Executor"
    app_description: str = "A web interface for executing recipes"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: Optional[int] = None  # Let Gradio find an available port

    # MCP settings
    mcp_server: bool = True

    # Recipe executor settings
    log_dir: str = "logs"
    log_level: str = "DEBUG"  # Use DEBUG, INFO, WARNING, ERROR, or CRITICAL

    # Example recipes paths
    example_recipes: List[str] = [
        "../../recipes/example_simple/test_recipe.json",
        "../../recipes/example_content_writer/generate_content.json",
        "../../recipes/example_brave_search/search.json",
    ]

    # Theme settings
    theme: str = "soft"  # Use "default", "soft", "glass", etc.

    model_config = SettingsConfigDict(
        env_prefix="RECIPE_EXEC_APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables like PYTHONPATH
    )

    def to_launch_kwargs(self) -> Dict[str, Any]:
        """Convert settings to kwargs for gradio launch() method."""
        return {
            "server_name": self.host,
            "server_port": self.port,
            "share": False,
            "pwa": True,
            "debug": self.debug,
            "mcp_server": self.mcp_server,
        }


# Create global settings instance
settings = Settings()
