"""UI components for the Recipe Tool Gradio app."""

import json
import logging
from typing import List, Optional, Tuple

import gradio as gr
import gradio.themes

# Import recipe-executor components
from recipe_executor_app.app import create_executor_block
from recipe_executor_app.core import RecipeExecutorCore

from recipe_tool_app.config import settings
from recipe_tool_app.core import RecipeToolCore

# Initialize logger
logger = logging.getLogger(__name__)


def build_create_recipe_tab() -> Tuple[
    gr.TextArea, gr.File, gr.File, gr.Textbox, gr.Button, gr.Code, gr.Markdown, gr.JSON
]:
    """Build the Create Recipe tab UI components.

    Returns:
        Tuple: (idea_text, idea_file, reference_files, create_context_vars, create_btn,
               create_output, preview_md, create_debug_context)
    """
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")

            with gr.Tabs():
                with gr.TabItem("Text Input"):
                    idea_text = gr.TextArea(label="Idea Text", placeholder="Enter your recipe idea here...", lines=10)

                with gr.TabItem("File Input"):
                    idea_file = gr.File(label="Idea File", file_types=[".md", ".txt"])

            with gr.Accordion("Additional Options", open=False):
                reference_files = gr.File(
                    label="Reference Files",
                    file_types=[".md", ".txt", ".py", ".json"],
                    file_count="multiple",
                )
                create_context_vars = gr.Textbox(
                    label="Context Variables",
                    placeholder="key1=value1,key2=value2",
                    info="Add context variables as key=value pairs, separated by commas",
                )

            create_btn = gr.Button("Create Recipe", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown("### Output")
            with gr.Tabs():
                with gr.TabItem("Generated Recipe"):
                    create_output = gr.Code(language="json", label="Recipe JSON", lines=20, wrap_lines=True)
                with gr.TabItem("Preview"):
                    preview_md = gr.Markdown(label="Recipe Structure")
                with gr.TabItem("Context"):
                    create_debug_context = gr.JSON(label="Context Variables")

    return (
        idea_text,
        idea_file,
        reference_files,
        create_context_vars,
        create_btn,
        create_output,
        preview_md,
        create_debug_context,
    )


def setup_create_recipe_events(
    recipe_core: RecipeToolCore,
    idea_text: gr.TextArea,
    idea_file: gr.File,
    reference_files: gr.File,
    context_vars: gr.Textbox,
    create_btn: gr.Button,
    create_output: gr.Code,
    preview_md: gr.Markdown,
    debug_context: gr.JSON,
) -> None:
    """Set up event handlers for create recipe tab.

    Args:
        recipe_core: RecipeToolCore instance
        idea_text: Idea text textarea
        idea_file: Idea file upload component
        reference_files: Reference files upload component
        context_vars: Context variables textbox
        create_btn: Create button
        create_output: Generated recipe code component
        preview_md: Recipe structure preview markdown
        debug_context: Debug context code component
    """

    async def create_recipe_formatted(
        text: str, file: Optional[str], refs: Optional[List[str]], ctx: Optional[str]
    ) -> Tuple[str, str, str]:
        """Format create_recipe output for Gradio UI."""
        result = await recipe_core.create_recipe(text, file, refs, ctx)
        # Extract the individual fields for Gradio UI
        recipe_json = result.get("recipe_json", "")
        structure_preview = result.get("structure_preview", "")
        # Format debug context as JSON string
        debug_context = json.dumps(result.get("debug_context", {}), indent=2, default=lambda o: str(o))
        return recipe_json, structure_preview, debug_context

    create_btn.click(
        fn=create_recipe_formatted,
        inputs=[idea_text, idea_file, reference_files, context_vars],
        outputs=[create_output, preview_md, debug_context],
        api_name="create_recipe",
    )


def build_ui(recipe_core: RecipeToolCore) -> gr.Blocks:
    """Build the complete Gradio UI.

    Args:
        recipe_core: RecipeToolCore instance for executing recipes

    Returns:
        gr.Blocks: Gradio Blocks interface
    """
    # Apply theme
    theme = gradio.themes.Soft() if settings.theme == "soft" else settings.theme

    with gr.Blocks(title=settings.app_title, theme=theme) as app:
        gr.Markdown("# Recipe Tool")
        gr.Markdown("A web interface for executing and creating recipes.")

        with gr.Tabs():
            # Create Recipe Tab
            with gr.TabItem("Create Recipe"):
                create_components = build_create_recipe_tab()
                (
                    idea_text,
                    idea_file,
                    reference_files,
                    create_context_vars,
                    create_btn,
                    create_output,
                    preview_md,
                    create_debug_context,
                ) = create_components

            # Use the dedicated recipe-executor component
            with gr.TabItem("Execute Recipe"):
                # Create a standalone recipe executor core
                executor_core = RecipeExecutorCore()

                # Create the executor block with no header (since we're in a tab)
                # We're using the block directly in the UI, so no need to assign it to a variable
                create_executor_block(executor_core, include_header=False)

                # Log success
                logger.info("Successfully created Recipe Executor component")

        # Set up event handlers for create recipe tab
        setup_create_recipe_events(
            recipe_core,
            idea_text,
            idea_file,
            reference_files,
            create_context_vars,
            create_btn,
            create_output,
            preview_md,
            create_debug_context,
        )

    return app
