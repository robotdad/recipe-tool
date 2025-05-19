"""
Reusable UI components for the Document Generator editor.
"""

import gradio as gr

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
    # Allow empty resource key if none selected
    res_dd = gr.Dropdown(choices=[""] + refs, label="Resource Key", value=resource_key)
    nested_acc = gr.Accordion(label="Subsections", open=False)
    return [title_tb, mode_radio, prompt_tb, refs_ch, res_dd, nested_acc]