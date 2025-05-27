"""UI components for the Recipe Tool app."""

from typing import Optional, Tuple

import gradio as gr

from .core import RecipeToolCore


def create_recipe_ui(core: RecipeToolCore) -> Tuple:
    """Create the Create Recipe UI components."""
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

    return (idea_text, idea_file, reference_files, context_vars, create_btn, recipe_output, preview_md, debug_context)
