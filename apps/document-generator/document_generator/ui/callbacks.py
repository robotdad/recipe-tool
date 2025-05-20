"""
Callback functions for the Document Generator editor UI.
"""

import json
import tempfile
import asyncio
from pathlib import Path

import gradio as gr  # type: ignore

from document_generator.executor.runner import generate_document
from document_generator.models.outline import Outline
from document_generator.ui.utils import (
    build_outline_data,
    make_resource_choices,
    make_section_choices,
)


def add_resource(res_list):
    res_list = res_list or []
    res_list.append({"key": "", "description": "", "path": "", "merge_mode": ""})
    choices = make_resource_choices(res_list)
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
    value = choices[-1] if choices else ""
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


def update_resource_list(res_list):
    choices = make_resource_choices(res_list)
    value = choices[-1] if choices else None
    return gr.update(choices=choices, value=value)


def update_section_key_choices(res_list):
    # Update refs and resource key dropdowns
    keys = make_resource_choices(res_list)
    return gr.update(choices=keys), gr.update(choices=keys)


def add_section(sec_list):
    sec_list = sec_list or []
    sec_list.append({"title": "", "prompt": "", "refs": [], "resource_key": None, "sections": []})
    choices = make_section_choices(sec_list)
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
    value = choices[-1] if choices else ""
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
        return "", "prompt", [], "", "", sec_list
    s = sec_list[idx]
    mode = "static" if s.get("resource_key") else "prompt"
    return (
        s.get("title", ""),
        mode,
        s.get("prompt", ""),
        s.get("refs", []),
        s.get("resource_key", ""),
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


def update_section_list(sec_list):
    choices = make_section_choices(sec_list)
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
    return [
        title,
        instr,
        res_list,
        sec_list,
        nested,
        gr.update(choices=res_choices, value=res_choices[-1] if res_choices else ""),
        gr.update(choices=sec_choices, value=sec_choices[-1] if sec_choices else ""),
    ]


def get_download_outline(title, instr, res_table, secs_table, nested):
    outline = build_outline_data(title, instr, res_table, secs_table, nested)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
    json.dump(outline, tmp, indent=2)
    tmp.close()
    return tmp.name


def generate_document_callback(title, instr, res_table, secs_table, nested):
    outline_dict = build_outline_data(title, instr, res_table, secs_table, nested)
    outline = Outline.from_dict(outline_dict)
    # Run async generation in a blocking context
    doc_text = asyncio.run(generate_document(outline))
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w")
    tmp.write(doc_text)
    tmp.close()
    return doc_text, tmp.name
