"""Configuration settings for the Recipe Executor app."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExampleRecipe(BaseModel):
    """Configuration for an example recipe."""

    name: str
    path: str
    context_vars: Dict[str, str] = {}


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

    # Example recipes with context
    example_recipes: List[ExampleRecipe] = [
        ExampleRecipe(
            name="Simple Test Recipe",
            path="../../recipes/example_simple/test_recipe.json",
            context_vars={},
        ),
        ExampleRecipe(
            name="Demo Quarterly Report",
            path="../../recipes/example_quarterly_report/demo_quarterly_report_recipe.json",
            context_vars={"new_data_file": "recipes/example_quarterly_report/demo-data/q2-2025-sales.csv"},
        ),
    ]

    # Theme settings
    theme: str = "soft"  # Use "default", "soft", "glass", etc.

    model_config = SettingsConfigDict(
        env_prefix="RECIPE_APP_",
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
