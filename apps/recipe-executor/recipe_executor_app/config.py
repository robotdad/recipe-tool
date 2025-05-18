"""Configuration settings for the Recipe Executor app."""

from typing import List, Dict, Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the Recipe Executor app."""

    # App settings
    app_title: str = "Recipe Executor"
    app_description: str = "A web interface for executing and creating recipes"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: int = 7861
    # Queue is enabled by default in Gradio

    # MCP settings
    mcp_server: bool = True

    # Recipe executor settings
    recipe_creator_path: str = "recipes/recipe_creator/create.json"
    log_dir: str = "logs"

    # Example recipes paths
    example_recipes: List[str] = [
        "recipes/example_simple/test_recipe.json",
        "recipes/example_content_writer/generate_content.json",
        "recipes/example_brave_search/search.json",
    ]

    # Theme settings
    theme: str = "soft"  # Use "default", "soft", "glass", etc.

    model_config = SettingsConfigDict(
        env_prefix="RECIPE_APP_", env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    def to_launch_kwargs(self) -> Dict[str, Any]:
        """Convert settings to kwargs for gradio launch() method."""
        return {
            "server_name": self.host,
            "server_port": self.port,
            "share": False,
            "debug": self.debug,
            "mcp_server": self.mcp_server,
        }


# Create global settings instance
settings = Settings()
