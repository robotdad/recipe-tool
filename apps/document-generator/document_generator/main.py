import json
import asyncio
from pathlib import Path
import tempfile

import gradio as gr

from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger


REPO_ROOT = Path(__file__).resolve().parents[3]
RECIPE_PATH = REPO_ROOT / "recipes" / "document_generator" / "document-generator-recipe.json"
DEFAULT_OUTLINE = REPO_ROOT / "recipes" / "document_generator" / "examples" / "readme.json"


def load_default_outline() -> str:
    try:
        return DEFAULT_OUTLINE.read_text()
    except FileNotFoundError:
        return "{}"


async def generate_document(outline_json: str) -> str:
    try:
        json.loads(outline_json)
    except json.JSONDecodeError as e:
        return f"Invalid JSON provided: {e}"

    with tempfile.TemporaryDirectory() as tmpdir:
        outline_path = Path(tmpdir) / "outline.json"
        outline_path.write_text(outline_json)

        logger = init_logger(log_dir=tmpdir)
        context = Context(artifacts={"outline_file": str(outline_path)})
        executor = Executor(logger)
        await executor.execute(str(RECIPE_PATH), context)
        return context.artifacts.get("document", "")


def main() -> None:
    outline_editor = gr.Code(label="Outline JSON", language="json", value=load_default_outline())
    output = gr.Markdown()

    demo = gr.Blocks()
    with demo:
        gr.Markdown("# Document Generator")
        outline_box = outline_editor
        gen_btn = gr.Button("Generate")
        gen_btn.click(generate_document, inputs=outline_box, outputs=output)
        output.render()
    demo.launch()


if __name__ == "__main__":
    asyncio.run(main())
