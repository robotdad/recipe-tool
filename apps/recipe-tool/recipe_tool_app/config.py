"""Configuration settings for the Recipe Tool app."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExampleIdea(BaseModel):
    """Configuration for an example recipe idea."""

    name: str
    path: str
    description: str = ""
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
    recipe_creator_path: str = "../../../recipes/recipe_creator/create.json"
    log_dir: str = "logs"
    log_level: str = (
        "DEBUG"  # Use DEBUG, INFO, WARNING, ERROR, or CRITICAL - Set to DEBUG for detailed path information
    )

    # Example recipes paths (for recipe executor)
    example_recipes: List[str] = [
        "../../../recipes/example_simple/test_recipe.json",
        "../../../recipes/example_content_writer/generate_content.json",
        "../../../recipes/example_brave_search/search.json",
    ]

    # Example ideas (for recipe creator)
    example_ideas: List[ExampleIdea] = [
        ExampleIdea(
            name="Hello World Gradio App",
            path="examples/hello-world-spec-idea.md",
            description="Create a simple Hello World app using Gradio",
        ),
        ExampleIdea(
            name="Simple Spec to Python",
            path="examples/simple-spec-recipe-idea.md",
            description="Turn a text spec into a runnable Python script",
            context_vars={
                "output_root": "./output",
            },
        ),
        ExampleIdea(
            name="Recipe to Mermaid Diagram",
            path="examples/recipe-to-mermaid-idea.md",
            description="Convert a recipe JSON into a Mermaid diagram",
        ),
        ExampleIdea(
            name="File Rollup Tool",
            path="examples/file-rollup-tool-idea.md",
            description="Create a tool that combines multiple files into one",
        ),
        ExampleIdea(
            name="Quarterly Report Generator",
            path="examples/demo-quarterly-report-idea.md",
            description="Generate a quarterly sales report from CSV data",
            context_vars={},
        ),
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
            "pwa": True,
            "debug": self.debug,
            "mcp_server": self.mcp_server,
        }


# Create global settings instance
settings = Settings()
