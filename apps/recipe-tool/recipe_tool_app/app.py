"""Gradio web app for the Recipe Tool."""

import argparse
from typing import Any

from recipe_executor.logger import init_logger

from recipe_tool_app.config import settings
from recipe_tool_app.core import RecipeToolCore
from recipe_tool_app.ui_components import build_ui

# Set up logging
logger = init_logger(settings.log_dir)
# Set logger level from settings
logger.setLevel(settings.log_level.upper())


def create_app() -> Any:
    """Create and return the Gradio app."""
    # Initialize the core functionality
    recipe_core = RecipeToolCore()

    # Build the UI around the core
    app = build_ui(recipe_core)

    return app


def main() -> None:
    """Entry point for the application."""
    # Parse command line arguments to override settings
    parser = argparse.ArgumentParser(description=settings.app_description)
    parser.add_argument("--host", help=f"Host to listen on (default: {settings.host})")
    parser.add_argument("--port", type=int, help=f"Port to listen on (default: {settings.port})")
    parser.add_argument("--no-mcp", action="store_true", help="Disable MCP server functionality")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    # Override settings with command line arguments if provided
    if args.host:
        settings.host = args.host
    if args.port:
        settings.port = args.port
    if args.no_mcp:
        settings.mcp_server = False
    if args.debug:
        settings.debug = True

    # Create and launch the app with settings
    app = create_app()

    # Get launch kwargs from settings
    launch_kwargs = settings.to_launch_kwargs()
    app.launch(**launch_kwargs)


if __name__ == "__main__":
    main()
