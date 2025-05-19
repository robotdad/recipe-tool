"""Gradio web app for the Recipe Executor."""

import argparse
from typing import Any, Dict, Optional

import gradio as gr
import gradio.themes
from recipe_executor.logger import init_logger

from recipe_executor_app.config import settings
from recipe_executor_app.core import RecipeExecutorCore
from recipe_executor_app.ui_components import (
    build_examples_tab,
    build_execute_recipe_tab,
    setup_example_events,
    setup_execute_recipe_events,
)

# Set up logging
logger = init_logger(settings.log_dir)
# Set logger level from settings
logger.setLevel(settings.log_level.upper())


def create_executor_block(recipe_core: Optional[RecipeExecutorCore] = None, include_header: bool = True) -> gr.Blocks:
    """Create a Recipe Executor block that can be embedded in other apps.

    Args:
        recipe_core: Optional RecipeExecutorCore instance. If None, a new one will be created.
        include_header: Whether to include the header (title and description)

    Returns:
        gr.Blocks: Gradio Blocks interface that can be embedded in other apps
    """
    # Initialize core if not provided
    if recipe_core is None:
        recipe_core = RecipeExecutorCore()

    # Apply theme
    theme = gradio.themes.Soft() if settings.theme == "soft" else settings.theme

    with gr.Blocks(theme=theme) as block:
        if include_header:
            gr.Markdown("# Recipe Executor")
            gr.Markdown("A web interface for executing recipes.")

        # Examples area (not in a tab)
        with gr.Accordion("Examples", open=False):
            examples_components = build_examples_tab()
            example_paths, load_example_btn, example_desc = examples_components

        # Execute Recipe Tab - since this is a component, no tabs needed
        execute_components = build_execute_recipe_tab()
        recipe_file, recipe_text, context_vars, execute_btn, result_output, raw_result, debug_context = (
            execute_components
        )

        # Set up event handlers for execute recipe
        setup_execute_recipe_events(
            recipe_core,
            recipe_file,
            recipe_text,
            context_vars,
            execute_btn,
            result_output,
            raw_result,
            debug_context,
        )

        # Set up example loading events
        setup_example_events(
            recipe_core,
            example_paths,
            load_example_btn,
            example_desc,
            recipe_text,
            context_vars,
        )

    return block


def create_app() -> gr.Blocks:
    """Create and return the Gradio app."""
    # Initialize the core functionality
    recipe_core = RecipeExecutorCore()

    # Create the app with a title
    with gr.Blocks(title=settings.app_title) as app:
        # Use the component approach - clean and reusable
        create_executor_block(recipe_core)

    return app


def get_components(recipe_core: Optional[RecipeExecutorCore] = None) -> Dict[str, Any]:
    """Return individual components for embedding in other apps.

    Args:
        recipe_core: Optional RecipeExecutorCore instance. If None, a new one will be created.

    Returns:
        Dict[str, Any]: Dictionary of components and functions that can be reused
    """
    # Initialize core if not provided
    if recipe_core is None:
        recipe_core = RecipeExecutorCore()

    return {
        "create_executor_block": create_executor_block,
        "core": recipe_core,
        "execute_recipe": recipe_core.execute_recipe,
        "load_recipe": recipe_core.load_recipe,
    }


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
