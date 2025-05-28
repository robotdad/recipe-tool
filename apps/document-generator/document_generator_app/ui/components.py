"""
All UI components for the simplified document generator.
"""
import gradio as gr


def create_resource_editor():
    """Resource editor form."""
    with gr.Column(visible=False) as container:
        gr.Markdown("### Resource Details")
        
        key = gr.Textbox(label="Resource Key", placeholder="unique_key")
        description = gr.TextArea(label="Description", lines=2)
        path = gr.Textbox(label="Path or URL", placeholder="https://... or /path/to/file")
        file_upload = gr.File(label="Or Upload File")
        merge_mode = gr.Dropdown(["concat", "dict"], label="Merge Mode", value="concat")
    
    return {
        "container": container,
        "key": key,
        "description": description,
        "path": path,
        "file": file_upload,
        "merge_mode": merge_mode
    }


def create_section_editor():
    """Section editor form."""
    with gr.Column(visible=False) as container:
        gr.Markdown("### Section Details")
        
        title = gr.Textbox(label="Section Title")
        mode = gr.Radio(["Prompt", "Static"], label="Mode", value="Prompt")
        
        # Prompt mode
        with gr.Column() as prompt_container:
            prompt = gr.TextArea(label="Generation Prompt", lines=4)
            refs = gr.CheckboxGroup(label="Reference Resources", choices=[])
        
        # Static mode
        with gr.Column(visible=False) as static_container:
            resource_key = gr.Dropdown(label="Source Resource", choices=[])
    
    return {
        "container": container,
        "title": title,
        "mode": mode,
        "prompt": prompt,
        "refs": refs,
        "resource_key": resource_key,
        "prompt_container": prompt_container,
        "static_container": static_container
    }