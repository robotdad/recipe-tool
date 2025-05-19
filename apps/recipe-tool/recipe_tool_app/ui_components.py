"""UI components for the Recipe Tool Gradio app."""

import json
import logging
from typing import List, Optional, Tuple

import gradio as gr
import gradio.themes

from recipe_tool_app.config import settings
from recipe_tool_app.core import RecipeToolCore

# Initialize logger
logger = logging.getLogger(__name__)


def build_execute_recipe_tab() -> Tuple[gr.File, gr.Code, gr.Textbox, gr.Button, gr.Markdown, gr.Code, gr.Code]:
    """Build the Execute Recipe tab UI components.

    Returns:
        Tuple: (recipe_file, recipe_text, context_vars, execute_btn,
               result_output, raw_result, debug_context)
    """
    with gr.TabItem("Execute Recipe"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Input")
                recipe_file = gr.File(label="Recipe JSON File", file_types=[".json"])
                recipe_text = gr.Code(label="Recipe JSON", language="json", lines=15)

                with gr.Accordion("Context Variables", open=False):
                    context_vars = gr.Textbox(
                        label="Context Variables",
                        placeholder="key1=value1,key2=value2",
                        info="Add context variables as key=value pairs, separated by commas",
                    )

                execute_btn = gr.Button("Execute Recipe", variant="primary")

            with gr.Column(scale=1):
                gr.Markdown("### Output")
                with gr.Tabs():
                    with gr.TabItem("Results"):
                        result_output = gr.Markdown(label="Results")
                    with gr.TabItem("Raw Output"):
                        raw_result = gr.Code(language="json", label="Raw JSON")
                    with gr.TabItem("Debug Context"):
                        debug_context = gr.Code(language="json", label="Full Context Variables")

    return (
        recipe_file,
        recipe_text,
        context_vars,
        execute_btn,
        result_output,
        raw_result,
        debug_context,
    )


def build_create_recipe_tab() -> Tuple[
    gr.TextArea, gr.File, gr.File, gr.Textbox, gr.Button, gr.Code, gr.Markdown, gr.Code
]:
    """Build the Create Recipe tab UI components.

    Returns:
        Tuple: (idea_text, idea_file, reference_files, create_context_vars, create_btn,
               create_output, preview_md, create_debug_context)
    """
    with gr.TabItem("Create Recipe"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Input")

                with gr.Tabs():
                    with gr.TabItem("Text Input"):
                        idea_text = gr.TextArea(
                            label="Idea Text", placeholder="Enter your recipe idea here...", lines=10
                        )

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
                        create_output = gr.Code(language="json", label="Recipe JSON", lines=20)
                    with gr.TabItem("Preview"):
                        preview_md = gr.Markdown(label="Recipe Structure")
                    with gr.TabItem("Debug Context"):
                        create_debug_context = gr.Code(language="json", label="Full Context Variables")

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


def build_examples_tab() -> Tuple[gr.Dropdown, gr.Button, gr.Markdown]:
    """Build the Examples tab UI components.

    Returns:
        Tuple: (example_paths, load_example_btn, example_desc)
    """
    with gr.TabItem("Examples"):
        gr.Markdown("### Recipe Examples")
        example_paths = gr.Dropdown(
            settings.example_recipes,
            label="Example Recipes",
        )
        load_example_btn = gr.Button("Load Example")

        with gr.Accordion("Example Description", open=False):
            example_desc = gr.Markdown()

    return example_paths, load_example_btn, example_desc


def setup_execute_recipe_events(
    recipe_core: RecipeToolCore,
    recipe_file: gr.File,
    recipe_text: gr.Code,
    context_vars: gr.Textbox,
    execute_btn: gr.Button,
    result_output: gr.Markdown,
    raw_result: gr.Code,
    debug_context: gr.Code,
) -> None:
    """Set up event handlers for execute recipe tab.

    Args:
        recipe_core: RecipeToolCore instance
        recipe_file: File upload component
        recipe_text: Recipe text code component
        context_vars: Context variables textbox
        execute_btn: Execute button
        result_output: Results markdown output
        raw_result: Raw JSON output code component
        debug_context: Debug context code component
    """

    async def execute_recipe_formatted(
        file: Optional[str], text: Optional[str], ctx: Optional[str]
    ) -> Tuple[str, str, str]:
        """Format execute_recipe output for Gradio UI."""
        result = await recipe_core.execute_recipe(file, text, ctx)
        # Extract the individual fields for Gradio UI
        formatted_results = result.get("formatted_results", "")
        raw_json = result.get("raw_json", "{}")
        # Format debug context as JSON string
        debug_context = json.dumps(result.get("debug_context", {}), indent=2, default=lambda o: str(o))
        return formatted_results, raw_json, debug_context

    execute_btn.click(
        fn=execute_recipe_formatted,
        inputs=[recipe_file, recipe_text, context_vars],
        outputs=[result_output, raw_result, debug_context],
        api_name="execute_recipe",
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
    debug_context: gr.Code,
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
            # Execute Recipe Tab
            execute_components = build_execute_recipe_tab()
            recipe_file, recipe_text, context_vars, execute_btn, result_output, raw_result, debug_context = (
                execute_components
            )

            # Create Recipe Tab
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

            # Examples Tab
            examples_components = build_examples_tab()
            example_paths, load_example_btn, example_desc = examples_components

        # Set up event handlers for execute recipe tab
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

        # Set up example loading events
        from recipe_tool_app.example_handler import load_example_formatted

        load_example_btn.click(
            fn=load_example_formatted,
            inputs=[example_paths],
            outputs=[recipe_text, example_desc],
            api_name="load_example",
        )

    return app
