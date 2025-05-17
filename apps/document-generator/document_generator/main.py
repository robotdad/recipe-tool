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


def load_default_outline() -> dict:
    """Return the default outline as a Python object."""
    try:
        return json.loads(DEFAULT_OUTLINE.read_text())
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


async def generate_document(outline: dict | None) -> str:
    """Generate a document from the provided outline object."""
    if not outline:
        return "No outline provided."
    outline_json = json.dumps(outline)

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

        output_root = Path(context.get("output_root", tmpdir))
        filename = context.get("document_filename")
        if not filename:
            return context.get("document", "")

        document_path = output_root / f"{filename}.md"
        try:
            return document_path.read_text()
        except FileNotFoundError:
            return f"Generated file not found: {document_path}"


def main() -> None:
    """Launch the Gradio interface for generating documents."""

    with gr.Blocks() as demo:
        gr.Markdown("# Document Generator")
        outline_editor = gr.JSON(label="Outline", value=load_default_outline())
        output = gr.Markdown()
        gen_btn = gr.Button("Generate")
        gen_btn.click(generate_document, inputs=outline_editor, outputs=output)

    demo.queue().launch()


if __name__ == "__main__":
    main()
