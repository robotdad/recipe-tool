import json
import tempfile
from pathlib import Path

import gradio as gr
from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger

REPO_ROOT = Path(__file__).resolve().parents[3]
RECIPE_PATH = REPO_ROOT / "recipes" / "document_generator" / "document-generator-recipe.json"
RECIPE_ROOT = RECIPE_PATH.parent
DEFAULT_OUTLINE = RECIPE_ROOT / "examples" / "readme.json"


def load_default_outline() -> str:
    try:
        return DEFAULT_OUTLINE.read_text()
    except FileNotFoundError:
        return "{}"


async def generate_document(outline_json: str | None) -> str:
    if not outline_json:
        return "No outline JSON provided."
    try:
        json.loads(outline_json)
    except json.JSONDecodeError as e:
        return f"Invalid JSON provided: {e}"

    with tempfile.TemporaryDirectory() as tmpdir:
        outline_path = Path(tmpdir) / "outline.json"
        outline_path.write_text(outline_json)

        logger = init_logger(log_dir=tmpdir)
        context = Context(
            artifacts={
                "outline_file": str(outline_path),
                "recipe_root": str(RECIPE_ROOT),
            }
        )
        executor = Executor(logger)
        await executor.execute(str(RECIPE_PATH), context)
        return context.get("document", "")


def main() -> None:
    """Launch the Gradio interface for generating documents."""

    css = ".code-wrap {white-space: pre-wrap;}"
    with gr.Blocks(css=css) as demo:
        gr.Markdown("# Document Generator")
        outline_box = gr.Code(
            label="Outline JSON",
            language="json",
            value=load_default_outline(),
            elem_classes="code-wrap",
        )
        output = gr.Markdown()
        gen_btn = gr.Button("Generate")
        gen_btn.click(generate_document, inputs=outline_box, outputs=output)

    demo.queue().launch()


if __name__ == "__main__":
    main()
