"""UI components for the Recipe Executor Gradio app."""

import json
import logging
import os
from typing import Optional, Tuple

import gradio as gr
import gradio.themes

from recipe_executor_app.config import settings
from recipe_executor_app.core import RecipeExecutorCore

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


def build_examples_tab() -> Tuple[gr.Dropdown, gr.Button, gr.Markdown]:
    """Build the Examples tab UI components.

    Returns:
        Tuple: (example_paths, load_example_btn, example_desc)
    """
    # Create components directly - no Tab or Markdown headings needed
    example_paths = gr.Dropdown(
        settings.example_recipes,
        label="Example Recipes",
    )
    load_example_btn = gr.Button("Load Example")
    example_desc = gr.Markdown()

    return example_paths, load_example_btn, example_desc


def setup_execute_recipe_events(
    recipe_core: RecipeExecutorCore,
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
        recipe_core: RecipeExecutorCore instance
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


def setup_example_events(
    recipe_core: RecipeExecutorCore,
    example_paths: gr.Dropdown,
    load_example_btn: gr.Button,
    example_desc: gr.Markdown,
    recipe_text: gr.Code,
    context_vars: Optional[gr.Textbox] = None,
) -> None:
    """Set up event handlers for examples tab.

    Args:
        recipe_core: RecipeExecutorCore instance
        example_paths: Example paths dropdown
        load_example_btn: Load example button
        example_desc: Example description markdown
        recipe_text: Recipe text code component
        context_vars: Optional context variables textbox
    """

    async def load_example_formatted(path: str) -> Tuple[str, str, Optional[str]]:
        """Format load_example output for Gradio UI."""
        result = await recipe_core.load_recipe(path)
        # Extract the individual fields for Gradio UI
        recipe_content = result.get("recipe_content", "")
        structure_preview = result.get("structure_preview", "")
        
        # Set recipe_root context variable for examples
        recipe_context_vars = None
        if context_vars is not None and path:
            # Get the directory containing the recipe
            recipe_dir = os.path.dirname(path)
            recipe_context_vars = f"recipe_root={recipe_dir}"
            
        return recipe_content, structure_preview, recipe_context_vars

    outputs = [recipe_text, example_desc]
    if context_vars is not None:
        outputs.append(context_vars)
        
    load_example_btn.click(
        fn=load_example_formatted,
        inputs=[example_paths],
        outputs=outputs,
        api_name="load_example",
    )


# Note: The build_ui function has been moved to app.py as create_executor_block
# to better support component reuse in other Gradio applications
