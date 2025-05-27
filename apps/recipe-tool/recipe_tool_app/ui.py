"""UI components for the Recipe Tool app."""

from typing import Optional, Tuple

import gradio as gr

from .core import RecipeToolCore


def create_recipe_ui(core: RecipeToolCore) -> Tuple:
    """Create the Create Recipe UI components."""
    from .config import settings

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")

            with gr.Tabs():
                with gr.TabItem("Upload Idea"):
                    idea_file = gr.File(label="Idea Text File", file_types=[".md", ".txt"])

                with gr.TabItem("Examples"):
                    # Create dropdown choices from example ideas
                    example_choices = [(ex.name, idx) for idx, ex in enumerate(settings.example_ideas)]
                    example_dropdown = gr.Dropdown(choices=example_choices, label="Example Ideas", type="index")
                    load_example_btn = gr.Button("Load Example", variant="secondary")

            idea_text = gr.Code(
                label="Idea Text",
                language="markdown",
                lines=10,
                max_lines=20,
                show_line_numbers=False,
                interactive=True,
                wrap_lines=True,
            )

            with gr.Accordion("Additional Options", open=False):
                reference_files = gr.File(
                    label="Reference Files",
                    file_types=[".md", ".txt", ".py", ".json"],
                    file_count="multiple",
                )
                context_vars = gr.Textbox(
                    label="Context Variables",
                    placeholder="key1=value1,key2=value2",
                    info="Add context variables as key=value pairs",
                )

            create_btn = gr.Button("Create Recipe", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown("### Output")
            with gr.Tabs():
                with gr.TabItem("Generated Recipe"):
                    recipe_output = gr.Code(language="json", label="Recipe JSON", lines=20, wrap_lines=True)
                with gr.TabItem("Preview"):
                    preview_md = gr.Markdown(label="Recipe Structure")
                with gr.TabItem("Context"):
                    debug_context = gr.JSON(label="Context Variables")

    # Set up event handler
    import asyncio

    def create_recipe_handler(text: str, file, refs, ctx: Optional[str]):
        """Wrapper to handle async function in Gradio."""
        try:
            # Handle Gradio file input
            file_path = file.name if file else None
            ref_paths = [f.name for f in refs] if refs else None

            # Use asyncio.run() which properly manages the event loop
            result = asyncio.run(core.create_recipe(text, file_path, ref_paths, ctx))
            return (
                result.get("recipe_json", ""),
                result.get("structure_preview", ""),
                result.get("debug_context", {}),
            )
        except Exception as e:
            import traceback

            error_msg = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            return ("", f"### Error\n```\n{error_msg}\n```", {"error": str(e)})

    create_btn.click(
        fn=create_recipe_handler,
        inputs=[idea_text, idea_file, reference_files, context_vars],
        outputs=[recipe_output, preview_md, debug_context],
        api_name="create_recipe",
    )

    # Set up example loading
    def load_example(example_idx):
        if example_idx is None:
            return "", ""

        example = settings.example_ideas[example_idx]

        # Read the example file content
        try:
            from pathlib import Path

            # Get the directory where this module is located
            module_dir = Path(__file__).parent.parent
            example_path = module_dir / example.path

            with open(example_path, "r") as f:
                content = f.read()
        except Exception as e:
            content = f"Error loading example: {str(e)}"

        # Convert context vars to string format
        ctx_parts = [f"{k}={v}" for k, v in example.context_vars.items()]
        ctx = ",".join(ctx_parts) if ctx_parts else ""

        return content, ctx

    load_example_btn.click(
        fn=load_example,
        inputs=[example_dropdown],
        outputs=[idea_text, context_vars],
    )

    # Load file content when a file is selected
    def load_file_content(file):
        if not file:
            return ""
        try:
            with open(file.name, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error loading file: {str(e)}"

    idea_file.change(
        fn=load_file_content,
        inputs=[idea_file],
        outputs=[idea_text],
    )

    return (idea_text, idea_file, reference_files, context_vars, create_btn, recipe_output, preview_md, debug_context)
