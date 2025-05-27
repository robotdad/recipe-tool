"""UI components for the Recipe Executor app."""

import io
import json
import logging

import gradio as gr

from recipe_executor_app.core import RecipeExecutorCore
from recipe_executor_app.utils import safe_json_dumps

logger = logging.getLogger(__name__)


def create_ui(core: RecipeExecutorCore, include_header: bool = True):
    """Create the Recipe Executor UI."""
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")

            # Examples section at the top for easy access
            with gr.Accordion("Examples", open=False):
                from recipe_executor_app.config import settings

                # Create dropdown choices from example recipes
                example_choices = [(ex.name, idx) for idx, ex in enumerate(settings.example_recipes)]
                example_dropdown = gr.Dropdown(choices=example_choices, label="Example Recipes", type="index")
                load_example_btn = gr.Button("Load Example", size="sm")
                example_desc = gr.Markdown()

            recipe_file = gr.File(label="Recipe JSON File", file_types=[".json"])
            recipe_text = gr.Code(label="Recipe JSON", language="json", interactive=True, lines=20)

            with gr.Accordion("Context Variables", open=False):
                context_vars = gr.Textbox(
                    placeholder="key1=value1,key2=value2", info="Add context variables as key=value pairs"
                )

            execute_btn = gr.Button("Execute Recipe", variant="primary", interactive=False)

        with gr.Column(scale=1):
            gr.Markdown("### Output")
            with gr.Tabs():
                with gr.TabItem("Results"):
                    result_output = gr.Markdown()
                    context_json = gr.JSON(label="Context")

                with gr.TabItem("Logs"):
                    logs_output = gr.Textbox(lines=20, max_lines=30, interactive=False)

    # Set up event handlers
    async def execute_with_logs(file, text, ctx, progress=gr.Progress()):
        """Execute recipe with log capture."""
        # Capture logs
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        handler.setLevel(logging.INFO)

        root_logger = logging.getLogger()
        root_logger.addHandler(handler)

        try:
            progress(0, desc="Executing recipe...")

            # Execute recipe with file path or text
            result = await core.execute_recipe(file, text, ctx)

            progress(1, desc="Complete!")

            # Get logs
            handler.flush()
            logs = log_capture.getvalue()

            # Format context
            context = safe_json_dumps(result.get("debug_context", {}))

            return (result.get("formatted_results", ""), logs, json.loads(context))
        finally:
            root_logger.removeHandler(handler)
            log_capture.close()

    execute_btn.click(
        fn=execute_with_logs,
        inputs=[recipe_file, recipe_text, context_vars],
        outputs=[result_output, logs_output, context_json],
        api_name="execute_recipe",
        show_progress="full",
    )

    # Enable button when recipe is loaded
    recipe_text.change(fn=lambda x: gr.update(interactive=bool(x)), inputs=[recipe_text], outputs=[execute_btn])

    # Load file content
    def load_file(file_path):
        if not file_path:
            return "", gr.update(interactive=False)
        try:
            with open(file_path, "r") as f:
                content = f.read()
            json.loads(content)  # Validate
            return content, gr.update(interactive=True)
        except Exception:
            return "", gr.update(interactive=False)

    recipe_file.change(fn=load_file, inputs=[recipe_file], outputs=[recipe_text, execute_btn])

    # Set up example loading
    async def load_example(example_idx):
        if example_idx is None:
            return "", "", ""

        example = settings.example_recipes[example_idx]

        # Load the recipe content
        result = await core.load_recipe(example.path)
        content = result.get("recipe_content", "")

        # Build preview with description
        preview = f"**{example.name}**"
        if example.description:
            preview += f": {example.description}"

        # Convert context vars to string format
        ctx_parts = [f"{k}={v}" for k, v in example.context_vars.items()]
        ctx = ",".join(ctx_parts) if ctx_parts else ""

        return content, preview, ctx

    load_example_btn.click(
        fn=load_example,
        inputs=[example_dropdown],
        outputs=[recipe_text, example_desc, context_vars],
    )

    return recipe_file, recipe_text, context_vars, execute_btn, result_output, logs_output, context_json
