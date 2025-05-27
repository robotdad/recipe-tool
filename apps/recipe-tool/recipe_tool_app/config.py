"""Configuration settings for the Recipe Tool app."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExampleIdea(BaseModel):
    """Configuration for an example recipe idea."""

    name: str
    path: str
    context_vars: Dict[str, str] = {}


class Settings(BaseSettings):
    """Configuration settings for the Recipe Tool app."""

    # App settings
    app_title: str = "Recipe Tool"
    app_description: str = "A web interface for executing and creating recipes"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: Optional[int] = None  # Let Gradio find an available port
    # Queue is enabled by default in Gradio

    # MCP settings
    mcp_server: bool = True

    # Recipe tool settings
    log_dir: str = "logs"
    log_level: str = (
        "DEBUG"  # Use DEBUG, INFO, WARNING, ERROR, or CRITICAL - Set to DEBUG for detailed path information
    )

    # Example ideas (for recipe creator)
    example_ideas: List[ExampleIdea] = [
        ExampleIdea(
            name="Hello World Gradio App",
            path="../../recipes/recipe_creator/examples/hello-world-spec-idea.md",
        ),
        ExampleIdea(
            name="Simple Spec to Python",
            path="../../recipes/recipe_creator/examples/simple-spec-recipe-idea.md",
            context_vars={
                "output_root": "./output",
            },
        ),
        ExampleIdea(
            name="Recipe to Mermaid Diagram",
            path="../../recipes/recipe_creator/examples/recipe-to-mermaid-idea.md",
        ),
        ExampleIdea(
            name="File Rollup Tool",
            path="../../recipes/recipe_creator/examples/file-rollup-tool-idea.md",
        ),
        ExampleIdea(
            name="Quarterly Report Generator",
            path="../../recipes/recipe_creator/examples/demo-quarterly-report-idea.md",
            context_vars={},
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
