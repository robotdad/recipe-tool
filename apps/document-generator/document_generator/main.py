import json
import tempfile
import urllib.request
from urllib.parse import urlparse
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, List

import gradio as gr
from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger

REPO_ROOT = Path(__file__).resolve().parents[3]
RECIPE_PATH = REPO_ROOT / "recipes" / "document_generator" / "document-generator-recipe.json"
RECIPE_ROOT = RECIPE_PATH.parent
DEFAULT_OUTLINE = RECIPE_ROOT / "examples" / "readme.json"


@dataclass
class Resource:
    key: str = ""
    path: str = ""
    description: str = ""
    merge_mode: str = "append"


@dataclass
class Section:
    title: str = ""
    prompt: str = ""
    refs: List[str] = field(default_factory=list)
    sections: List["Section"] = field(default_factory=list)


@dataclass
class Outline:
    title: str = ""
    general_instruction: str = ""
    resources: List[Resource] = field(default_factory=list)
    sections: List[Section] = field(default_factory=list)


def section_from_dict(data: dict) -> Section:
    return Section(
        title=data.get("title", ""),
        prompt=data.get("prompt", ""),
        refs=list(data.get("refs", [])),
        sections=[section_from_dict(s) for s in data.get("sections", [])],
    )


def resource_from_dict(data: dict) -> Resource:
    return Resource(
        key=data.get("key", ""),
        path=data.get("path", ""),
        description=data.get("description", ""),
        merge_mode=data.get("merge_mode", "append"),
    )


def outline_from_dict(data: dict) -> Outline:
    return Outline(
        title=data.get("title", ""),
        general_instruction=data.get("general_instruction", ""),
        resources=[resource_from_dict(r) for r in data.get("resources", [])],
        sections=[section_from_dict(s) for s in data.get("sections", [])],
    )


def outline_to_dict(outline: Outline) -> dict:
    return asdict(outline)


def load_default_outline() -> Outline:
    try:
        data = json.loads(DEFAULT_OUTLINE.read_text())
    except FileNotFoundError:
        data = {}
    return outline_from_dict(data)


async def generate_document(outline: Outline) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Resolve resources: download URLs or resolve local paths
        for res in outline.resources:
            if res.path:
                parsed = urlparse(res.path)
                if parsed.scheme in ("http", "https"):
                    dest = Path(tmpdir) / Path(parsed.path).name
                    urllib.request.urlretrieve(res.path, dest)
                    res.path = str(dest)
                else:
                    p = Path(res.path)
                    if not p.exists():
                        p2 = RECIPE_ROOT / res.path
                        if p2.exists():
                            res.path = str(p2)
                    else:
                        res.path = str(p)

        data = outline_to_dict(outline)
        outline_json = json.dumps(data, indent=2)
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

    outline = load_default_outline()

    with gr.Blocks(css=".code-wrap {white-space: pre-wrap;}") as demo:
        gr.Markdown("# Document Generator")

        gr.Markdown("## Metadata")
        title_tb = gr.Textbox(value=outline.title, label="Title")
        instruction_tb = gr.TextArea(value=outline.general_instruction, label="General Instruction")

        gr.Markdown("## Resources")
        resource_inputs: List[Any] = []
        for res in outline.resources:
            with gr.Accordion(res.key or "Resource", open=False):
                key_tb = gr.Textbox(value=res.key, label="Key")
                desc_tb = gr.Textbox(value=res.description, label="Description")
                path_tb = gr.Textbox(value=res.path, label="Path or URL")
                initial_file = None
                if res.path:
                    p = Path(res.path)
                    if not p.exists():
                        p = RECIPE_ROOT / res.path
                    if p.exists():
                        initial_file = str(p)
                file_tb = gr.File(label="File", value=initial_file)
                resource_inputs.extend([key_tb, desc_tb, path_tb, file_tb])

        gr.Markdown("## Sections")
        section_inputs: List[Any] = []

        def render_section(sec: Section) -> None:
            with gr.Accordion(sec.title or "Section", open=False):
                title = gr.Textbox(value=sec.title, label="Title")
                prompt = gr.TextArea(value=sec.prompt, label="Prompt")
                refs = gr.CheckboxGroup(
                    choices=[r.key for r in outline.resources],
                    value=sec.refs,
                    label="Resource Refs",
                )
                section_inputs.extend([title, prompt, refs])
                for child in sec.sections:
                    render_section(child)

        for section in outline.sections:
            render_section(section)

        output = gr.Markdown()

        gen_btn = gr.Button("Generate")

        async def collect_and_generate(*vals: Any) -> str:
            idx = 0
            o = Outline(title=vals[idx], general_instruction=vals[idx + 1])
            idx += 2

            resources: List[Resource] = []
            for _ in outline.resources:
                key, desc, path_or_url, file_obj = (vals[idx], vals[idx + 1], vals[idx + 2], vals[idx + 3])
                idx += 4
                if file_obj:
                    path = file_obj.name
                else:
                    path = path_or_url or ""
                resources.append(Resource(key=key, path=path, description=desc))
            o.resources = resources

            def build_sections(sections_src: List[Section]) -> List[Section]:
                nonlocal idx
                result: List[Section] = []
                for sec in sections_src:
                    title = vals[idx]
                    prompt = vals[idx + 1]
                    refs = vals[idx + 2] or []
                    idx += 3
                    child = Section(title=title, prompt=prompt, refs=list(refs))
                    child.sections = build_sections(sec.sections)
                    result.append(child)
                return result

            o.sections = build_sections(outline.sections)
            return await generate_document(o)

        gen_btn.click(
            collect_and_generate,
            inputs=[title_tb, instruction_tb] + resource_inputs + section_inputs,
            outputs=output,
        )

    demo.queue().launch()


if __name__ == "__main__":
    main()
