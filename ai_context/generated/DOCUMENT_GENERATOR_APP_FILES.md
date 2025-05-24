# apps/document-generator/document_generator_app

[collect-files]

**Search:** ['apps/document-generator/document_generator_app']
**Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output']
**Include:** []
**Date:** 5/23/2025, 12:34:00 PM
**Files:** 19

=== File: apps/document-generator/document_generator_app/__init__.py ===


=== File: apps/document-generator/document_generator_app/cli/__init__.py ===
"""
CLI package for Document Generator.
"""

__all__ = ["app"]
from .main import app


=== File: apps/document-generator/document_generator_app/cli/__main__.py ===
"""
CLI entrypoint for Document Generator.
"""

from .main import app

if __name__ == "__main__":
    app()


=== File: apps/document-generator/document_generator_app/cli/main.py ===
"""
CLI for headless document generation.
"""

import json
import asyncio
from pathlib import Path

import typer  # type: ignore

from ..models.outline import Outline
from ..executor.runner import generate_document

app = typer.Typer(no_args_is_help=False)


@app.command()
def generate(
    outline_file: str = typer.Option(..., "--outline", "-o", help="Path to outline JSON file"),
    output_file: str = typer.Option(None, "--output", "-O", help="Path to write generated Markdown"),
):
    """
    Generate a document from the given outline JSON.
    """
    # Load and validate outline
    try:
        raw = Path(outline_file).read_text()
        data = json.loads(raw)
        outline = Outline.from_dict(data)
    except Exception as e:
        typer.secho(f"Failed to load outline: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    # Generate document
    try:
        doc_text = asyncio.run(generate_document(outline))
    except Exception as e:
        typer.secho(f"Generation failed: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    # Output
    if output_file:
        try:
            Path(output_file).write_text(doc_text)
            typer.secho(f"Document written to {output_file}", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"Failed to write document: {e}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
    else:
        typer.echo(doc_text)
    raise typer.Exit(code=0)


if __name__ == "__main__":
    # Entry point for CLI
    app()


=== File: apps/document-generator/document_generator_app/config/__init__.py ===
"""
Config package for Document Generator.
"""

__all__ = ["Settings"]
from .settings import Settings


=== File: apps/document-generator/document_generator_app/config/settings.py ===
"""
Configuration and environment-based settings for Document Generator.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env in current directory if present
env_path = Path(__file__).parents[2] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


class Settings:
    """Load settings from environment variables."""

    def __init__(self):
        # Default model
        self.model_name = os.environ.get("MODEL_NAME", "gpt-4")
        # API key
        self.api_key = os.environ.get("API_KEY", "")


=== File: apps/document-generator/document_generator_app/executor/__init__.py ===
"""
Executor package for Document Generator.
"""

__all__ = ["generate_document"]
from .runner import generate_document


=== File: apps/document-generator/document_generator_app/executor/runner.py ===
"""
Headless generation runner: invoke the document-generator recipe.
"""

import json
import tempfile
from pathlib import Path

from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger

from ..models.outline import Outline


from typing import Optional


async def generate_document(outline: Optional[Outline]) -> str:
    """
    Run the document-generator recipe with the given outline and return the generated Markdown.
    """
    # Allow stub invocation without an outline for initial tests
    if outline is None:
        return ""
    from urllib.parse import urlparse
    import urllib.request

    REPO_ROOT = Path(__file__).resolve().parents[4]
    RECIPE_PATH = REPO_ROOT / "recipes" / "document_generator" / "document_generator_recipe.json"
    RECIPE_ROOT = RECIPE_PATH.parent

    with tempfile.TemporaryDirectory() as tmpdir:
        # Resolve resource paths: download URLs or locate local files
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

        data = outline.to_dict()
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


=== File: apps/document-generator/document_generator_app/main.py ===
"""
Main entrypoint for the Document Generator App UI.
"""

from document_generator_app.ui.layout import build_editor


def main() -> None:
    """Launch the Gradio interface for editing and generating documents."""
    build_editor().launch(mcp_server=True, pwa=True)


if __name__ == "__main__":
    main()


=== File: apps/document-generator/document_generator_app/models/__init__.py ===
"""
Models package for Document Generator.
"""

__all__ = ["Resource", "Section", "Outline"]
from .outline import Resource, Section, Outline


=== File: apps/document-generator/document_generator_app/models/outline.py ===
"""
Data models for the Document Generator app.
Defines Resource, Section, and Outline dataclasses with serialization utilities.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any


@dataclass
class Resource:
    key: str
    path: str
    description: str
    merge_mode: str


@dataclass
class Section:
    title: str
    prompt: Optional[str] = None
    refs: List[str] = field(default_factory=list)
    resource_key: Optional[str] = None
    sections: List["Section"] = field(default_factory=list)


def section_from_dict(data: Dict[str, Any]) -> Section:
    return Section(
        title=data.get("title", ""),
        prompt=data.get("prompt"),
        refs=list(data.get("refs", [])),
        resource_key=data.get("resource_key"),
        sections=[section_from_dict(s) for s in data.get("sections", [])],
    )


@dataclass
class Outline:
    title: str
    general_instruction: str
    resources: List[Resource] = field(default_factory=list)
    sections: List[Section] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Outline":
        res_list: List[Resource] = []
        for r in data.get("resources", []):
            res_list.append(
                Resource(
                    key=r.get("key", ""),
                    path=r.get("path", ""),
                    description=r.get("description", ""),
                    merge_mode=r.get("merge_mode", "concat"),
                )
            )
        sec_list: List[Section] = [section_from_dict(s) for s in data.get("sections", [])]
        return cls(
            title=data.get("title", ""),
            general_instruction=data.get("general_instruction", ""),
            resources=res_list,
            sections=sec_list,
        )


=== File: apps/document-generator/document_generator_app/schema/__init__.py ===
"""
Schema package for Document Generator.
"""

__all__ = ["validate_outline"]
from .validator import validate_outline


=== File: apps/document-generator/document_generator_app/schema/outline_schema.json ===
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Outline",
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "general_instruction": {"type": "string"},
    "resources": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "key": {"type": "string"},
          "path": {"type": "string"},
          "description": {"type": "string"},
          "merge_mode": {"type": "string", "enum": ["concat", "dict"]}
        },
        "required": ["key", "path", "description"],
        "additionalProperties": false
      }
    },
    "sections": {
      "type": "array",
      "items": {"$ref": "#/definitions/section"}
    }
  },
  "definitions": {
    "section": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "prompt": {"type": "string"},
        "refs": {"type": "array", "items": {"type": "string"}},
        "resource_key": {"type": "string"},
        "sections": {"type": "array", "items": {"$ref": "#/definitions/section"}}
      },
      "required": ["title"],
      "oneOf": [
        {"required": ["prompt"]},
        {"required": ["resource_key"]}
      ],
      "additionalProperties": false
    }
  },
  "required": ["title", "general_instruction", "resources", "sections"],
  "additionalProperties": false
}

=== File: apps/document-generator/document_generator_app/schema/validator.py ===
"""
Schema validation utilities for outline JSON.
"""

import json
from pathlib import Path

from jsonschema import validate

_SCHEMA_PATH = Path(__file__).parent / "outline_schema.json"


def validate_outline(data: dict) -> None:
    """
    Validate outline data against the JSON schema.
    Raises jsonschema.ValidationError on failure.
    """
    schema_text = _SCHEMA_PATH.read_text()
    schema = json.loads(schema_text)
    validate(instance=data, schema=schema)


=== File: apps/document-generator/document_generator_app/ui/__init__.py ===
"""
UI package for Document Generator.
"""

__all__ = ["build_editor", "resource_entry", "section_entry"]
from .layout import build_editor
from .components import resource_entry, section_entry


=== File: apps/document-generator/document_generator_app/ui/callbacks.py ===
"""
Callback functions for the Document Generator editor UI.
"""

import json
import tempfile
import asyncio
from pathlib import Path

import gradio as gr  # type: ignore

from document_generator_app.executor.runner import generate_document
from document_generator_app.models.outline import Outline
from document_generator_app.ui.utils import (
    build_outline_data,
    make_resource_choices,
    make_section_choices,
)


def add_resource(res_list):
    res_list = res_list or []
    res_list.append({"key": "", "description": "", "path": "", "merge_mode": ""})
    choices = make_resource_choices(res_list)
    # When adding a new resource, we want to select it
    value = choices[-1] if choices else ""
    return res_list, gr.update(choices=choices, value=value)


def remove_resource(res_list, selection):
    res_list = res_list or []
    idx = None
    # find index by label or numeric
    if selection:
        if selection.isdigit():
            idx = int(selection)
        else:
            for i, r in enumerate(res_list):
                if r.get("key", "") == selection:
                    idx = i
                    break
    if isinstance(idx, int) and 0 <= idx < len(res_list):
        res_list.pop(idx)
    choices = make_resource_choices(res_list)
    value = choices[0] if choices else ""  # Select first item after removal
    return res_list, gr.update(choices=choices, value=value)


def select_resource(selection, res_list):
    # Return fields and updated state
    res_list = res_list or []
    idx = None
    if selection:
        if selection.isdigit():
            idx = int(selection)
        else:
            for i, r in enumerate(res_list):
                if r.get("key", "") == selection:
                    idx = i
                    break
    if idx is None or idx < 0 or idx >= len(res_list):
        return "", "", None, "", "", res_list
    r = res_list[idx]
    return (
        r.get("key", ""),
        r.get("description", ""),
        r.get("path", ""),
        None,
        r.get("merge_mode", ""),
        res_list,
    )


def update_resource_key(value, selection, res_list):
    idx = None
    if selection:
        if selection.isdigit():
            idx = int(selection)
        else:
            for i, r in enumerate(res_list or []):
                if r.get("key", "") == selection:
                    idx = i
                    break
    if isinstance(idx, int) and 0 <= idx < len(res_list):
        res_list[idx]["key"] = value
    return res_list


def update_resource_description(value, selection, res_list):
    idx = None
    if selection:
        if selection.isdigit():
            idx = int(selection)
        else:
            for i, r in enumerate(res_list or []):
                if r.get("key", "") == selection:
                    idx = i
                    break
    if isinstance(idx, int) and 0 <= idx < len(res_list):
        res_list[idx]["description"] = value
    return res_list


def update_resource_path(value, selection, res_list):
    idx = None
    if selection:
        if selection.isdigit():
            idx = int(selection)
        else:
            for i, r in enumerate(res_list or []):
                if r.get("key", "") == selection:
                    idx = i
                    break
    if isinstance(idx, int) and 0 <= idx < len(res_list):
        res_list[idx]["path"] = value
    return res_list


def upload_resource_file(file_obj, selection, res_list):
    if not file_obj or not selection:
        return res_list
    idx = None
    if selection.isdigit():
        idx = int(selection)
    else:
        for i, r in enumerate(res_list or []):
            if r.get("key", "") == selection:
                idx = i
                break
    if isinstance(idx, int) and 0 <= idx < len(res_list):
        res_list[idx]["path"] = file_obj.name
    return res_list


def update_resource_merge_mode(value, selection, res_list):
    idx = None
    if selection:
        if selection.isdigit():
            idx = int(selection)
        else:
            for i, r in enumerate(res_list or []):
                if r.get("key", "") == selection:
                    idx = i
                    break
    if isinstance(idx, int) and 0 <= idx < len(res_list):
        res_list[idx]["merge_mode"] = value
    return res_list


def update_resource_list(res_list, current_selection=None):
    choices = make_resource_choices(res_list)
    # Keep current selection if it exists in the new choices
    if current_selection in choices:
        value = current_selection
    else:
        value = choices[-1] if choices else None
    return gr.update(choices=choices, value=value)


def update_section_key_choices(res_list, current_refs=None, current_resource_key=None):
    # Update refs and resource key dropdowns
    keys = make_resource_choices(res_list)

    # For refs, preserve the current selection if possible
    refs_update = gr.update(choices=keys)
    if current_refs is not None:
        # Filter to keep only values that exist in new keys
        preserved_refs = [ref for ref in current_refs if ref in keys]
        refs_update = gr.update(choices=keys, value=preserved_refs)

    # For resource key, preserve the current selection if it exists in the new choices
    res_key_update = gr.update(choices=keys)
    if current_resource_key is not None and current_resource_key in keys:
        res_key_update = gr.update(choices=keys, value=current_resource_key)

    return refs_update, res_key_update


def add_section(sec_list):
    sec_list = sec_list or []
    sec_list.append({"title": "", "prompt": "", "refs": [], "resource_key": None, "sections": []})
    choices = make_section_choices(sec_list)
    # When adding a new section, we want to select it
    value = choices[-1] if choices else ""
    return sec_list, gr.update(choices=choices, value=value)


def remove_section(sec_list, selection):
    sec_list = sec_list or []
    idx = None
    if selection:
        if selection.isdigit():
            idx = int(selection)
        else:
            for i, s in enumerate(sec_list or []):
                if s.get("title", "") == selection:
                    idx = i
                    break
    if isinstance(idx, int) and 0 <= idx < len(sec_list):
        sec_list.pop(idx)
    choices = make_section_choices(sec_list)
    value = choices[0] if choices else ""  # Select first item after removal
    return sec_list, gr.update(choices=choices, value=value)


def select_section(selection, sec_list):
    sec_list = sec_list or []
    idx = None
    if selection:
        if selection.isdigit():
            idx = int(selection)
        else:
            for i, s in enumerate(sec_list):
                if s.get("title", "") == selection:
                    idx = i
                    break
    if idx is None or idx < 0 or idx >= len(sec_list):
        return "", "prompt", "", [], "", sec_list
    s = sec_list[idx]
    mode = "static" if s.get("resource_key") else "prompt"

    # Get section values, with safe defaults
    title = s.get("title", "")
    prompt = s.get("prompt", "")
    refs = s.get("refs", [])
    resource_key = s.get("resource_key", "")

    return (
        title,
        mode,
        prompt,
        refs,
        resource_key,
        sec_list,
    )


def update_section_title(value, selection, sec_list):
    idx = None
    if selection:
        if selection.isdigit():
            idx = int(selection)
        else:
            for i, s in enumerate(sec_list or []):
                if s.get("title", "") == selection:
                    idx = i
                    break
    if isinstance(idx, int) and 0 <= idx < len(sec_list):
        sec_list[idx]["title"] = value
    return sec_list


def update_section_mode(value, selection, sec_list):
    idx = None
    if selection:
        if selection.isdigit():
            idx = int(selection)
        else:
            for i, s in enumerate(sec_list or []):
                if s.get("title", "") == selection:
                    idx = i
                    break
    if isinstance(idx, int) and 0 <= idx < len(sec_list):
        if value == "prompt":
            sec_list[idx].pop("resource_key", None)
        else:
            sec_list[idx].pop("prompt", None)
            sec_list[idx].pop("refs", None)
    return sec_list


def update_section_prompt(value, selection, sec_list):
    idx = None
    if selection:
        if selection.isdigit():
            idx = int(selection)
        else:
            for i, s in enumerate(sec_list or []):
                if s.get("title", "") == selection:
                    idx = i
                    break
    if isinstance(idx, int) and 0 <= idx < len(sec_list):
        sec_list[idx]["prompt"] = value
    return sec_list


def update_section_refs(value, selection, sec_list):
    idx = None
    if selection:
        if selection.isdigit():
            idx = int(selection)
        else:
            for i, s in enumerate(sec_list or []):
                if s.get("title", "") == selection:
                    idx = i
                    break
    if isinstance(idx, int) and 0 <= idx < len(sec_list):
        sec_list[idx]["refs"] = value
    return sec_list


def update_section_resource_key(value, selection, sec_list):
    idx = None
    if selection:
        if selection.isdigit():
            idx = int(selection)
        else:
            for i, s in enumerate(sec_list or []):
                if s.get("title", "") == selection:
                    idx = i
                    break
    if isinstance(idx, int) and 0 <= idx < len(sec_list):
        sec_list[idx]["resource_key"] = value
    return sec_list


def update_section_list(sec_list, current_selection=None):
    choices = make_section_choices(sec_list)
    # Keep current selection if it exists in the new choices
    if current_selection in choices:
        value = current_selection
    else:
        value = choices[-1] if choices else None
    return gr.update(choices=choices, value=value)


def get_uploaded_outline(file_obj):
    if not file_obj:
        return ["", "", [], [], []]
    raw = Path(file_obj.name).read_text()
    data = json.loads(raw)
    # Build state tables
    title = data.get("title", "")
    instr = data.get("general_instruction", "")
    res_list = data.get("resources", [])
    sec_list = data.get("sections", [])
    nested = [s.get("sections", []) for s in sec_list]
    res_choices = make_resource_choices(res_list)
    sec_choices = make_section_choices(sec_list)

    # Select the first item when uploading an outline (instead of the last)
    res_value = res_choices[0] if res_choices else None
    sec_value = sec_choices[0] if sec_choices else None

    return [
        title,
        instr,
        res_list,
        sec_list,
        nested,
        gr.update(choices=res_choices, value=res_value),
        gr.update(choices=sec_choices, value=sec_value),
    ]


def get_download_outline(title, instr, res_table, secs_table, nested):
    outline = build_outline_data(title, instr, res_table, secs_table, nested)

    # Create a filename based on the title
    filename = title.lower().replace(" ", "-")
    # Remove any non-alphanumeric or dash characters
    filename = "".join(c for c in filename if c.isalnum() or c == "-")
    # Ensure we have a valid filename
    if not filename:
        filename = "outline"

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
    json.dump(outline, tmp, indent=2)
    tmp.close()

    # Return the file path with custom filename for DownloadButton
    return {"name": f"{filename}.json", "path": tmp.name}


def generate_document_callback(title, instr, res_table, secs_table, nested):
    outline_dict = build_outline_data(title, instr, res_table, secs_table, nested)
    outline = Outline.from_dict(outline_dict)
    # Run async generation in a blocking context
    doc_text = asyncio.run(generate_document(outline))

    # Create a filename based on the title
    filename = title.lower().replace(" ", "-")
    # Remove any non-alphanumeric or dash characters
    filename = "".join(c for c in filename if c.isalnum() or c == "-")
    # Ensure we have a valid filename
    if not filename:
        filename = "document"

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w")
    tmp.write(doc_text)
    tmp.close()

    # Return the document text and file path for the DownloadButton with visibility update
    return doc_text, gr.update(value={"name": f"{filename}.md", "path": tmp.name}, visible=True)


=== File: apps/document-generator/document_generator_app/ui/components.py ===
"""
Reusable UI components for the Document Generator editor.
"""

import gradio as gr  # type: ignore


def resource_entry(key: str = "", description: str = "", path: str = "", merge_mode: str = "concat"):
    """
    Return Gradio components for a single resource entry row.
    """
    key_tb = gr.Textbox(label="Key", value=key)
    desc_tb = gr.Textbox(label="Description", value=description)
    path_tb = gr.Textbox(label="Path or URL", value=path)
    file_upl = gr.File(label="Upload File")
    # Allow empty merge_mode selection
    mm_dd = gr.Dropdown(choices=["", "concat", "dict"], label="Merge Mode", value=merge_mode)
    return [key_tb, desc_tb, path_tb, file_upl, mm_dd]


def section_entry(section=None):
    """
    Return Gradio components for a single section entry, including nested placeholder.
    """
    section = section or {}
    title = section.get("title", "")
    prompt = section.get("prompt", "") or ""
    refs = section.get("refs", [])
    resource_key = section.get("resource_key", "") or ""

    title_tb = gr.Textbox(label="Section Title", value=title)
    mode = "prompt" if section.get("prompt") is not None else "static"
    mode_radio = gr.Radio(choices=["prompt", "static"], label="Mode", value=mode)
    prompt_tb = gr.TextArea(label="Prompt", value=prompt)
    refs_ch = gr.CheckboxGroup(choices=refs, label="Refs", value=refs)

    # Build dropdown choices, ensuring it includes the resource_key if present
    dropdown_choices = [""]
    if refs:
        dropdown_choices.extend(refs)
    if resource_key and resource_key not in dropdown_choices:
        dropdown_choices.append(resource_key)

    # Allow empty resource key if none selected
    res_dd = gr.Dropdown(
        choices=dropdown_choices,
        label="Resource Key",
        value=resource_key,
        allow_custom_value=True,  # Allow custom values to avoid warnings
    )
    nested_acc = gr.Accordion(label="Subsections", open=False)
    return [title_tb, mode_radio, prompt_tb, refs_ch, res_dd, nested_acc]


=== File: apps/document-generator/document_generator_app/ui/layout.py ===
"""
Two-column layout for the Document Generator editor using Gradio Blocks.
"""

import gradio as gr
import gradio.themes

from document_generator_app.ui.callbacks import (
    add_resource,
    add_section,
    generate_document_callback,
    get_download_outline,
    get_uploaded_outline,
    remove_resource,
    remove_section,
    select_resource,
    select_section,
    update_resource_description,
    update_resource_key,
    update_resource_list,
    update_resource_merge_mode,
    update_resource_path,
    update_section_key_choices,
    update_section_list,
    update_section_mode,
    update_section_prompt,
    update_section_refs,
    update_section_resource_key,
    update_section_title,
    upload_resource_file,
)
from document_generator_app.ui.components import resource_entry, section_entry
from document_generator_app.ui.utils import validate_outline_and_get_data


def build_editor() -> gr.Blocks:
    """
    Build and return the full Gradio Blocks interface with a two-column layout.
    """
    with gr.Blocks(title="Document Generator", theme=gradio.themes.Citrus()) as demo:
        # Persistent state for resources and sections
        initial_resources = []
        initial_sections = []
        resources_state = gr.State(initial_resources)
        sections_state = gr.State(initial_sections)
        nested_state = gr.State(initial_sections)

        gr.Markdown("# Document Generator")
        with gr.Row():
            with gr.Column():
                gr.Markdown("## Outline Editor")
                # Metadata
                title_tb = gr.Textbox(label="Title", placeholder="Document title")
                instruction_tb = gr.TextArea(label="General Instruction", placeholder="General instruction")

                # Resources block: selector + editor
                with gr.Accordion("Resources", open=True):
                    resources_list = gr.Dropdown(
                        choices=[], label="Select Resource", interactive=True, allow_custom_value=True
                    )
                    add_res_btn = gr.Button("Add Resource")
                    remove_res_btn = gr.Button("Remove Resource")
                    with gr.Column(visible=False) as resource_detail_panel:
                        key_tb, desc_tb, path_tb, file_upload, merge_mode_dd = resource_entry()

                # Sections block: selector + editor
                with gr.Accordion("Sections", open=True):
                    sections_list = gr.Dropdown(
                        choices=[], label="Select Section", interactive=True, allow_custom_value=True
                    )
                    add_sec_btn = gr.Button("Add Section")
                    remove_sec_btn = gr.Button("Remove Section")
                    with gr.Column(visible=False) as section_detail_panel:
                        sec_title_tb, mode_radio, sec_prompt_tb, sec_refs, sec_res_dd, nested_acc = section_entry()

            with gr.Column():
                gr.Markdown("## Document Generation")
                # Upload, Validate, Preview, Download Outline
                upload_outline_button = gr.File(label="Upload Outline JSON", file_types=[".json"])
                validate_btn = gr.Button("Validate Outline")
                validate_output = gr.Textbox(label="Validation Result")
                json_preview = gr.JSON(label="Outline JSON Preview")

                # Use DownloadButton for direct downloads
                download_outline_button = gr.DownloadButton("Download Outline JSON", variant="primary")

                # Generate button after validation
                generate_btn = gr.Button("Generate Document")
                # Generation output controls
                output_md = gr.Markdown(label="Generated Document")

                # Use DownloadButton for document download
                download_doc_button = gr.DownloadButton("Download Generated Document", variant="primary", visible=False)

        # Hook up resource callbacks
        add_res_btn.click(add_resource, inputs=[resources_state], outputs=[resources_state, resources_list])
        remove_res_btn.click(
            remove_resource, inputs=[resources_state, resources_list], outputs=[resources_state, resources_list]
        )
        resources_list.change(
            select_resource,
            inputs=[resources_list, resources_state],
            outputs=[key_tb, desc_tb, path_tb, file_upload, merge_mode_dd, resources_state],
        )
        # Show/hide resource detail panel based on selection
        resources_list.change(
            lambda sel: gr.update(visible=bool(sel)),
            inputs=[resources_list],
            outputs=[resource_detail_panel],
        )
        key_tb.change(update_resource_key, inputs=[key_tb, resources_list, resources_state], outputs=[resources_state])
        desc_tb.change(
            update_resource_description, inputs=[desc_tb, resources_list, resources_state], outputs=[resources_state]
        )
        path_tb.change(
            update_resource_path, inputs=[path_tb, resources_list, resources_state], outputs=[resources_state]
        )
        file_upload.change(
            upload_resource_file, inputs=[file_upload, resources_list, resources_state], outputs=[resources_state]
        )
        merge_mode_dd.change(
            update_resource_merge_mode,
            inputs=[merge_mode_dd, resources_list, resources_state],
            outputs=[resources_state],
        )
        resources_state.change(update_resource_list, inputs=[resources_state, resources_list], outputs=[resources_list])
        resources_state.change(
            update_section_key_choices, inputs=[resources_state, sec_refs, sec_res_dd], outputs=[sec_refs, sec_res_dd]
        )

        # Hook up section callbacks
        add_sec_btn.click(add_section, inputs=[sections_state], outputs=[sections_state, sections_list])
        remove_sec_btn.click(
            remove_section, inputs=[sections_state, sections_list], outputs=[sections_state, sections_list]
        )
        sections_state.change(update_section_list, inputs=[sections_state, sections_list], outputs=[sections_list])
        sections_list.change(
            select_section,
            inputs=[sections_list, sections_state],
            outputs=[sec_title_tb, mode_radio, sec_prompt_tb, sec_refs, sec_res_dd, sections_state],
        )
        # Show/hide section detail panel based on selection
        sections_list.change(
            lambda sel: gr.update(visible=bool(sel)),
            inputs=[sections_list],
            outputs=[section_detail_panel],
        )
        sec_title_tb.change(
            update_section_title, inputs=[sec_title_tb, sections_list, sections_state], outputs=[sections_state]
        )
        mode_radio.change(
            update_section_mode, inputs=[mode_radio, sections_list, sections_state], outputs=[sections_state]
        )
        sec_prompt_tb.change(
            update_section_prompt, inputs=[sec_prompt_tb, sections_list, sections_state], outputs=[sections_state]
        )
        sec_refs.change(update_section_refs, inputs=[sec_refs, sections_list, sections_state], outputs=[sections_state])
        sec_res_dd.change(
            update_section_resource_key, inputs=[sec_res_dd, sections_list, sections_state], outputs=[sections_state]
        )

        # Upload and validation callbacks
        upload_outline_button.upload(
            get_uploaded_outline,
            inputs=[upload_outline_button],
            outputs=[
                title_tb,
                instruction_tb,
                resources_state,
                sections_state,
                nested_state,
                resources_list,
                sections_list,
            ],
        )
        validate_btn.click(
            validate_outline_and_get_data,
            inputs=[title_tb, instruction_tb, resources_state, sections_state, nested_state],
            outputs=[validate_output, json_preview],
        )
        # Connect validate button to also update the download button with the file path
        validate_btn.click(
            get_download_outline,
            inputs=[title_tb, instruction_tb, resources_state, sections_state, nested_state],
            outputs=[download_outline_button],
        )

        # Also connect the download button directly so users can click it without validating first
        download_outline_button.click(
            get_download_outline,
            inputs=[title_tb, instruction_tb, resources_state, sections_state, nested_state],
            outputs=[download_outline_button],
        )

        # Generate document callback
        generate_btn.click(
            generate_document_callback,
            inputs=[title_tb, instruction_tb, resources_state, sections_state, nested_state],
            outputs=[output_md, download_doc_button],
        )

        # No need to add handlers for the DownloadButton - they work automatically when value is set
    return demo


=== File: apps/document-generator/document_generator_app/ui/utils.py ===
"""
Utility functions for the Document Generator editor brick.
"""

from document_generator_app.schema.validator import validate_outline


def build_outline_data(title, instr, res_table, secs_table, nested):
    """
    Build the outline dict from editor state: title, instruction, resources table,
    sections table, and nested subsections. Skips fully empty rows.
    """
    title_val = (title or "").strip()
    instr_val = (instr or "").strip()

    # Resources
    resources = []
    for r in res_table or []:
        key = r.get("key", "").strip()
        desc = r.get("description", "").strip()
        path = r.get("path", "").strip()
        mm = r.get("merge_mode", "")

        # Skip completely empty resources
        if not key and not desc and not path:
            continue

        resource = {"key": key, "description": desc, "path": path}
        if mm and mm.strip():
            resource["merge_mode"] = mm.strip()
        resources.append(resource)

    # Sections
    sections = []
    for idx, s in enumerate(secs_table or []):
        title_s = s.get("title", "").strip()
        prompt_s = s.get("prompt", "")
        refs_list = s.get("refs", [])
        rk = s.get("resource_key", "")

        # Convert values to proper types and strip whitespace
        if prompt_s is not None:
            prompt_s = str(prompt_s).strip()
        if rk is not None:
            rk = str(rk).strip()

        # Get subsections from nested state if available
        subs = []
        if nested and idx < len(nested):
            subs = nested[idx]

        # Skip completely empty sections
        if not title_s and not prompt_s and not refs_list and not rk and not subs:
            continue

        sec = {"title": title_s}

        # Add prompt and refs if in prompt mode
        if prompt_s:
            sec["prompt"] = prompt_s
            if refs_list:
                # Ensure refs is a list of strings
                if isinstance(refs_list, str):
                    refs = [r.strip() for r in refs_list.split(",") if r.strip()]
                else:
                    refs = [str(r).strip() for r in refs_list if r]
                sec["refs"] = refs
        # Add resource_key if in static mode
        elif rk:
            sec["resource_key"] = rk

        # Add subsections if present
        if subs:
            sec["sections"] = subs

        sections.append(sec)

    return {
        "title": title_val,
        "general_instruction": instr_val,
        "resources": resources,
        "sections": sections,
    }


def validate_outline_and_get_data(title, instr, res_table, secs_table, nested):
    """
    Build and validate the outline, returning (message, outline_dict).
    """
    outline = build_outline_data(title, instr, res_table, secs_table, nested)
    errors = []
    # Required top-level
    if not outline["title"]:
        errors.append("Title is required.")
    if not outline["general_instruction"]:
        errors.append("General instruction is required.")
    # Resource checks
    valid_keys = [r.get("key", "") for r in outline.get("resources", [])]
    for idx, r in enumerate(outline.get("resources", [])):
        if not r.get("key"):
            errors.append(f"Resource {idx} missing key.")
        if not r.get("description"):
            errors.append(f"Resource {idx} missing description.")
        if not r.get("path"):
            errors.append(f"Resource {idx} missing path.")
    # Sections exist
    if not outline.get("sections", []):
        errors.append("At least one section is required.")
    # Section checks
    for idx, sec in enumerate(outline.get("sections", [])):
        if not sec.get("title"):
            errors.append(f"Section {idx} missing title.")
        has_prompt = "prompt" in sec
        has_rk = "resource_key" in sec
        if has_prompt:
            for ref in sec.get("refs", []):
                if ref not in valid_keys:
                    errors.append(f"Section {idx} references unknown resource '{ref}'.")
        elif has_rk:
            if sec.get("resource_key") not in valid_keys:
                errors.append(f"Section {idx} references unknown resource '{sec.get('resource_key')}'.")
        else:
            errors.append(f"Section {idx} must have either a prompt or a resource key.")
    # Final result
    if errors:
        return "Validation error: " + "; ".join(errors), outline
    try:
        validate_outline(outline)
        return "Outline is valid.", outline
    except Exception as e:
        return f"Validation error: {e}", outline


def make_resource_choices(res_list):
    """
    Generate dropdown choices: resource keys or index if key empty.
    Returns list of strings for gr.Dropdown.
    """
    choices = []
    for idx, r in enumerate(res_list or []):
        key = r.get("key", "") if isinstance(r, dict) else ""
        choices.append(key.strip() or str(idx))
    return choices


def make_section_choices(sec_list):
    """
    Generate dropdown choices: section titles or index if title empty.
    Returns list of strings for gr.Dropdown.
    """
    choices = []
    for idx, s in enumerate(sec_list or []):
        title = s.get("title", "") if isinstance(s, dict) else ""
        choices.append(title.strip() or str(idx))
    return choices


