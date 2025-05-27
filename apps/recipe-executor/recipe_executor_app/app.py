"""Recipe Executor Gradio app."""

import argparse
from typing import Any, Dict, Optional

import gradio as gr
import gradio.themes  # type: ignore
from recipe_executor.logger import init_logger

from recipe_executor_app.config import settings
from recipe_executor_app.core import RecipeExecutorCore
from recipe_executor_app.ui import create_ui

# Set up logging
logger = init_logger(settings.log_dir)
logger.setLevel(settings.log_level.upper())


def create_executor_block(core: Optional[RecipeExecutorCore] = None, include_header: bool = True) -> gr.Blocks:
    """Create a reusable Recipe Executor block."""
    if core is None:
        core = RecipeExecutorCore()

    theme = gr.themes.Soft() if settings.theme == "soft" else None  # type: ignore

    with gr.Blocks(theme=theme) as block:
        if include_header:
            gr.Markdown("# Recipe Executor")
            gr.Markdown("A web interface for executing recipes.")

        # Main UI (now includes examples)
        create_ui(core, include_header)

    return block


def create_app() -> gr.Blocks:
    """Create the full Gradio app."""
    core = RecipeExecutorCore()

    with gr.Blocks(title=settings.app_title) as app:
        create_executor_block(core)

    return app


def get_components(core: Optional[RecipeExecutorCore] = None) -> Dict[str, Any]:
    """Get reusable components for embedding."""
    if core is None:
        core = RecipeExecutorCore()

    return {
        "create_executor_block": create_executor_block,
        "core": core,
        "execute_recipe": core.execute_recipe,
        "load_recipe": core.load_recipe,
    }


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=settings.app_description)
    parser.add_argument("--host", help=f"Host (default: {settings.host})")
    parser.add_argument("--port", type=int, help="Port")
    parser.add_argument("--no-mcp", action="store_true", help="Disable MCP")
    parser.add_argument("--debug", action="store_true", help="Debug mode")

    args = parser.parse_args()

    # Override settings
    if args.host:
        settings.host = args.host
    if args.port:
        settings.port = args.port
    if args.no_mcp:
        settings.mcp_server = False
    if args.debug:
        settings.debug = True

    # Launch app
    app = create_app()
    app.launch(**settings.to_launch_kwargs())


if __name__ == "__main__":
    main()
