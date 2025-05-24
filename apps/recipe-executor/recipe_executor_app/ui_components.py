"""UI components for the Recipe Executor Gradio app."""

import logging
import os
import io
import json
from typing import Optional, Tuple

import gradio as gr

from recipe_executor_app.config import settings
from recipe_executor_app.core import RecipeExecutorCore
from recipe_executor_app.utils import safe_json_serialize

# Initialize logger
logger = logging.getLogger(__name__)


def build_execute_recipe_tab() -> Tuple[
    gr.File, gr.Code, gr.Textbox, gr.Button, gr.Progress, gr.Markdown, gr.Textbox, gr.JSON
]:
    """Build the Execute Recipe tab UI components.

    Returns:
        Tuple: (recipe_file, recipe_text, context_vars, execute_btn,
               progress, result_output, logs_output, context_json)
    """
    # Create a progress bar first to ensure it's properly initialized
    progress = gr.Progress(track_tqdm=True)

    # No tab needed since this is the only component
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")
            recipe_file = gr.File(label="Recipe JSON File", file_types=[".json"])
            recipe_text = gr.Code(label="Recipe JSON", language="json", interactive=True, wrap_lines=True, lines=25)

            with gr.Accordion("Context Variables", open=False):
                context_vars = gr.Textbox(
                    label="Context Variables",
                    placeholder="key1=value1,key2=value2",
                    info="Add context variables as key=value pairs, separated by commas",
                )

            execute_btn = gr.Button("Execute Recipe", variant="primary", interactive=False)

        with gr.Column(scale=1):
            gr.Markdown("### Output")
            # No status indicator needed here

            with gr.Tabs():
                with gr.TabItem("Results"):
                    # The main results output
                    result_output = gr.Markdown(label="Results")

                    # Add context variables below the results
                    gr.Markdown("### Context Variables", visible=True)
                    context_json = gr.JSON(label="Context")

                with gr.TabItem("Logs"):
                    logs_output = gr.Textbox(label="Execution Logs", interactive=False, lines=20, max_lines=30)

    return (
        recipe_file,
        recipe_text,
        context_vars,
        execute_btn,
        progress,
        result_output,
        logs_output,
        context_json,
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
    progress: gr.Progress,
    result_output: gr.Markdown,
    logs_output: gr.Textbox,
    context_json: gr.JSON,
) -> None:
    """Set up event handlers for execute recipe tab.

    Args:
        recipe_core: RecipeExecutorCore instance
        recipe_file: File upload component
        recipe_text: Recipe JSON component
        context_vars: Context variables textbox
        execute_btn: Execute button
        progress: Progress indicator
        result_output: Results markdown output
        logs_output: Logs textbox output
        context_json: Context variables JSON component
    """

    async def execute_recipe_formatted(
        file: Optional[str], recipe_text: Optional[str], ctx: Optional[str], progress=gr.Progress()
    ) -> Tuple[str, str, str]:
        """Format execute_recipe output for Gradio UI."""
        # Create a log capture handler
        log_capture = io.StringIO()
        log_handler = logging.StreamHandler(log_capture)
        log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_handler.setFormatter(log_formatter)
        log_handler.setLevel(logging.INFO)  # Capture INFO level and above

        # Add the handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(log_handler)

        try:
            # Update progress bar
            progress(0, desc="Starting recipe execution...")

            # Parse the recipe text to JSON if needed
            recipe_json = json.loads(recipe_text) if recipe_text else None
            # Execute the recipe with log capturing
            result = await recipe_core.execute_recipe(file, recipe_json, ctx)

            # Update progress to indicate completion
            progress(1, desc="Recipe execution complete!")

            # Extract the individual fields for Gradio UI
            formatted_results = result.get("formatted_results", "")

            # Get the captured logs
            log_handler.flush()
            log_content = log_capture.getvalue()

            # Use the log content directly since we're using gr.Code with language="log"
            logs_formatted = log_content

            # Format the context as JSON string for gr.Code using our safe serializer
            debug_context_dict = result.get("debug_context", {})
            safe_context = safe_json_serialize(debug_context_dict)
            context_json_str = json.dumps(safe_context, indent=2)

            return formatted_results, logs_formatted, context_json_str
        finally:
            # Remove our handler to avoid duplication and memory leaks
            root_logger.removeHandler(log_handler)
            log_capture.close()

    # Using the global progress bar instead of a local indicator

    # Function to enable/disable execute button based on recipe content
    def update_execute_btn(recipe_content):
        # Enable button if recipe_content is not empty
        return gr.update(interactive=bool(recipe_content))

    # Set up event handler for recipe execution
    execute_btn.click(
        fn=execute_recipe_formatted,
        inputs=[recipe_file, recipe_text, context_vars],
        outputs=[result_output, logs_output, context_json],
        api_name="execute_recipe",
        show_progress="full",  # Show the progress bar during execution
    )

    # Enable execute button when recipe is loaded
    recipe_text.change(
        fn=update_execute_btn,
        inputs=[recipe_text],
        outputs=[execute_btn],
    )

    # When a file is uploaded, read the content and update the recipe_text
    def handle_file_upload(file_path):
        if file_path is None or not file_path:
            return "", gr.update(interactive=False)
        try:
            with open(file_path, "r") as f:
                content = f.read()
            # Validate JSON
            json.loads(content)
            return content, gr.update(interactive=True)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error parsing uploaded file: {e}")
            return "", gr.update(interactive=False)

    # Handle file upload to update JSON content and button state
    recipe_file.change(
        fn=handle_file_upload,
        inputs=[recipe_file],
        outputs=[recipe_text, execute_btn],
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
        recipe_text: Recipe JSON component
        context_vars: Optional context variables textbox
    """

    async def load_example_formatted(path: str) -> Tuple[str, str, Optional[str]]:
        """Format load_example output for Gradio UI."""
        result = await recipe_core.load_recipe(path)
        # Extract the individual fields for Gradio UI
        recipe_content_str = result.get("recipe_content", "")
        structure_preview = result.get("structure_preview", "")

        # Return the string content directly for gr.Code component
        recipe_content = recipe_content_str

        # Validate that it's valid JSON
        try:
            if recipe_content_str:
                json.loads(recipe_content_str)
        except json.JSONDecodeError:
            recipe_content = ""
            structure_preview = "### Error\nInvalid JSON in recipe file"

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
