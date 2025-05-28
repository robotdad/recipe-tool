"""
Main layout for the simplified Document Generator UI.
"""
import gradio as gr
import json
from pathlib import Path

from document_generator_app.ui.components import (
    create_resource_editor,
    create_section_editor
)
from document_generator_app.ui.callbacks import (
    create_initial_state,
    select_item,
    add_resource,
    add_section,
    save_item,
    remove_selected
)
from document_generator_app.ui.utils import validate_outline_data
from document_generator_app.executor.runner import generate_document
from document_generator_app.models.outline import Outline


def build_editor() -> gr.Blocks:
    """Create the main Gradio Blocks application."""
    
    # Simple CSS to ensure radio buttons display vertically
    custom_css = """
    .radio-vertical .wrap {
        flex-direction: column;
    }
    """
    
    with gr.Blocks(title="Document Generator", theme="soft", css=custom_css) as app:
        # Initialize state
        state = gr.State(create_initial_state())
        
        gr.Markdown("# Document Generator")
        gr.Markdown("Create structured documents with AI assistance")
        
        with gr.Row():
            # Left Column - Lists
            with gr.Column(scale=2, min_width=300):
                # Document metadata
                title = gr.Textbox(
                    label="Document Title",
                    placeholder="Enter your document title..."
                )
                instructions = gr.TextArea(
                    label="General Instructions",
                    placeholder="Overall guidance for document generation...",
                    lines=3
                )
                
                # Resources section
                with gr.Group():
                    gr.Markdown("### Resources")
                    with gr.Row():
                        resource_add_btn = gr.Button("+ Add", size="sm")
                        resource_remove_btn = gr.Button("- Remove", size="sm")
                    
                    resource_radio = gr.Radio(
                        label=None,
                        choices=[],
                        container=False,
                        elem_id="resource_radio",
                        elem_classes=["radio-vertical"]
                    )
                
                # Sections section  
                with gr.Group():
                    gr.Markdown("### Sections")
                    gr.Markdown("*Note: Changing resource keys may require re-selecting sections that reference them*", elem_classes=["markdown-small"])
                    with gr.Row():
                        section_add_btn = gr.Button("+ Add", size="sm")
                        section_sub_btn = gr.Button("+ Sub", size="sm")
                        section_remove_btn = gr.Button("- Remove", size="sm")
                    
                    section_radio = gr.Radio(
                        label=None,
                        choices=[],
                        container=False,
                        elem_id="section_radio",
                        elem_classes=["radio-vertical"]
                    )
                
                # Action buttons
                with gr.Row():
                    upload_btn = gr.UploadButton("Upload Outline", file_types=[".json"])
                    download_btn = gr.Button("Download Outline")
                    validate_btn = gr.Button("Validate")
                
                validation_message = gr.Markdown(visible=False)
            
            # Right Column - Editor
            with gr.Column(scale=3, min_width=400):
                # Empty state
                empty_state = gr.Markdown("### Select an item to edit", visible=True)
                
                # Editors
                resource_editor = create_resource_editor()
                section_editor = create_section_editor()
                
                # Generation section
                gr.Markdown("---")
                with gr.Row():
                    generate_btn = gr.Button(
                        "Generate Document",
                        variant="primary",
                        scale=2
                    )
                    preview_btn = gr.Button("Preview JSON", scale=1)
                
                # Output area
                output_container = gr.Column(visible=False)
                with output_container:
                    output_markdown = gr.Markdown()
                    download_doc_btn = gr.DownloadButton(
                        "Download Document",
                        visible=False
                    )
        
        # Helper functions
        def generate_resource_choices(state_data):
            """Generate choices for resource radio."""
            if not state_data or not state_data["outline"].resources:
                return []
            
            choices = []
            for i, res in enumerate(state_data["outline"].resources):
                label = res.key or f"Resource {i+1}"
                value = f"resource_{i}"
                choices.append((label, value))
            return choices
        
        def generate_section_choices(state_data):
            """Generate choices for section radio with indentation."""
            if not state_data or not state_data["outline"].sections:
                return []
            
            choices = []
            
            def add_sections(sections, path=None, level=0):
                if path is None:
                    path = []
                
                for i, sec in enumerate(sections):
                    if level >= 4:  # Max 4 levels
                        continue
                    
                    current_path = path + [i]
                    # Use non-breaking spaces for indentation that won't collapse
                    if level == 0:
                        indent = ""
                    elif level == 1:
                        indent = "└─ "  # No spaces before level 1
                    else:
                        # \u00A0 is a non-breaking space, 6 per level after level 1
                        indent = "\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0" * (level - 1) + "└─ "
                    
                    section_label = sec.title or f"Section {'.'.join(map(str, current_path))}"
                    label = f"{indent}{section_label}"
                    value = f"section_{'_'.join(map(str, current_path))}"
                    choices.append((label, value))
                    
                    # Add subsections
                    if sec.sections and level < 3:
                        add_sections(sec.sections, current_path, level + 1)
            
            add_sections(state_data["outline"].sections)
            return choices
        
        def update_lists(state_data):
            """Update both radio lists based on state."""
            resource_choices = generate_resource_choices(state_data)
            section_choices = generate_section_choices(state_data)
            
            # Get current selection
            selected_value = None
            if state_data["selected_type"] == "resource":
                selected_value = state_data["selected_id"]
            
            return (
                gr.update(choices=resource_choices, value=selected_value if state_data["selected_type"] == "resource" else None),
                gr.update(choices=section_choices, value=state_data["selected_id"] if state_data["selected_type"] == "section" else None)
            )
        
        def handle_selection(selected_id, selected_type, current_state):
            """Handle radio selection."""
            if not selected_id:
                # Clear selection
                current_state["selected_id"] = None
                current_state["selected_type"] = None
                return [
                    current_state,
                    gr.update(),
                    gr.update(),
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(visible=False),
                    "", "", "", "concat",
                    "", "Prompt", "", [], ""
                ]
            
            # Update state
            new_state = select_item(selected_id, selected_type, current_state)
            
            # Update UI visibility
            show_resource = selected_type == "resource"
            show_section = selected_type == "section"
            
            # Default values
            res_key = ""
            res_desc = ""
            res_path = ""
            res_merge = "concat"
            sec_title = ""
            sec_mode = "Prompt"
            sec_prompt = ""
            sec_refs = []
            sec_resource_key = ""
            
            # Update resource editor values
            if show_resource:
                idx = int(selected_id.split("_")[1])
                if idx < len(new_state["outline"].resources):
                    res = new_state["outline"].resources[idx]
                    res_key = res.key or ""
                    res_desc = res.description or ""
                    res_path = res.path or ""
                    res_merge = res.merge_mode or "concat"
            
            # Update section editor values
            if show_section:
                from document_generator_app.ui.utils import get_section_at_path
                path = [int(p) for p in selected_id.split("_")[1:]]
                sec = get_section_at_path(new_state["outline"].sections, path)
                if sec:
                    sec_title = sec.title or ""
                    sec_mode = "Static" if sec.resource_key else "Prompt"
                    sec_prompt = sec.prompt or ""
                    # Filter out refs that no longer exist
                    valid_keys = [r.key for r in new_state["outline"].resources if r.key]
                    sec_refs = [ref for ref in (sec.refs or []) if ref in valid_keys]
                    sec_resource_key = sec.resource_key or ""
            
            # Update radio choices - explicitly set which one should be selected
            resource_choices = generate_resource_choices(new_state)
            section_choices = generate_section_choices(new_state)
            
            # Only the radio for the selected type should have a value
            resource_value = new_state["selected_id"] if selected_type == "resource" else None
            section_value = new_state["selected_id"] if selected_type == "section" else None
            
            return [
                new_state,
                gr.update(choices=resource_choices, value=resource_value),
                gr.update(choices=section_choices, value=section_value),
                gr.update(visible=not (show_resource or show_section)),
                gr.update(visible=show_resource),
                gr.update(visible=show_section),
                res_key,
                res_desc,
                res_path,
                res_merge,
                sec_title,
                sec_mode,
                sec_prompt,
                gr.update(
                    choices=[r.key for r in new_state["outline"].resources if r.key],
                    value=sec_refs if sec_refs else []
                ),
                gr.update(
                    choices=[r.key for r in new_state["outline"].resources if r.key],
                    value=sec_resource_key if sec_resource_key and sec_resource_key in [r.key for r in new_state["outline"].resources if r.key] else None
                )
            ]
        
        # Helper to handle resource selection without updating own radio
        def handle_resource_click(val, current_state):
            if not val:
                return [current_state] + [gr.update()] * 14
            result = handle_selection(val, "resource", current_state)
            # Don't update the resource radio itself (index 1)
            result[1] = gr.update()
            return result
        
        # Helper to handle section selection without updating own radio
        def handle_section_click(val, current_state):
            if not val:
                return [current_state] + [gr.update()] * 14
            result = handle_selection(val, "section", current_state)
            # Don't update the section radio itself (index 2)
            result[2] = gr.update()
            return result
        
        # Connect radio selections
        resource_radio.change(
            handle_resource_click,
            inputs=[resource_radio, state],
            outputs=[
                state, resource_radio, section_radio, empty_state,
                resource_editor["container"], section_editor["container"],
                resource_editor["key"], resource_editor["description"],
                resource_editor["path"], resource_editor["merge_mode"],
                section_editor["title"], section_editor["mode"],
                section_editor["prompt"], section_editor["refs"],
                section_editor["resource_key"]
            ]
        )
        
        section_radio.change(
            handle_section_click,
            inputs=[section_radio, state],
            outputs=[
                state, resource_radio, section_radio, empty_state,
                resource_editor["container"], section_editor["container"],
                resource_editor["key"], resource_editor["description"],
                resource_editor["path"], resource_editor["merge_mode"],
                section_editor["title"], section_editor["mode"],
                section_editor["prompt"], section_editor["refs"],
                section_editor["resource_key"]
            ]
        )
        
        # Update metadata
        def update_metadata(state_data, doc_title, doc_instructions):
            """Update document metadata in state."""
            if state_data:
                state_data["outline"].title = doc_title or ""
                state_data["outline"].general_instruction = doc_instructions or ""
            resource_choices, section_choices = update_lists(state_data)
            return state_data, resource_choices, section_choices
        
        title.change(
            update_metadata,
            inputs=[state, title, instructions],
            outputs=[state, resource_radio, section_radio]
        )
        
        instructions.change(
            update_metadata,
            inputs=[state, title, instructions],
            outputs=[state, resource_radio, section_radio]
        )
        
        # Add resource handler
        def handle_add_resource(current_state):
            """Add a new resource."""
            new_state = add_resource(current_state)
            return handle_selection(
                new_state["selected_id"],
                new_state["selected_type"],
                new_state
            )
        
        # Add section handler
        def handle_add_section(current_state, as_subsection=False):
            """Add a new section."""
            new_state = add_section(current_state, as_subsection)
            return handle_selection(
                new_state["selected_id"],
                new_state["selected_type"],
                new_state
            )
        
        # Auto-save handlers
        def auto_save_resource_field(field_name, value, current_state):
            """Auto-save a resource field."""
            if not current_state["selected_id"] or current_state["selected_type"] != "resource":
                return current_state, gr.update(), gr.update()
            
            # Get current resource data
            idx = int(current_state["selected_id"].split("_")[1])
            if idx >= len(current_state["outline"].resources):
                return current_state, gr.update(), gr.update()
            
            # Update the specific field
            resource = current_state["outline"].resources[idx]
            setattr(resource, field_name, value)
            
            # Update radio choices to reflect new labels
            resource_choices = generate_resource_choices(current_state)
            section_choices = generate_section_choices(current_state)
            
            # If changing a resource key, we need to handle potential ref conflicts
            # The simplest approach: just update the radios, let the user re-select if needed
            if field_name == "key":
                # Clear any section selection to avoid ref conflicts
                return (
                    current_state,
                    gr.update(choices=resource_choices, value=current_state["selected_id"]),
                    gr.update(choices=section_choices, value=None)
                )
            
            return (
                current_state,
                gr.update(choices=resource_choices, value=current_state["selected_id"]),
                gr.update(choices=section_choices)
            )
        
        def auto_save_section_field(field_name, value, current_state):
            """Auto-save a section field."""
            if not current_state["selected_id"] or current_state["selected_type"] != "section":
                return current_state, gr.update(), gr.update()
            
            # Get current section
            from document_generator_app.ui.utils import get_section_at_path
            path = [int(p) for p in current_state["selected_id"].split("_")[1:]]
            section = get_section_at_path(current_state["outline"].sections, path)
            
            if not section:
                return current_state, gr.update(), gr.update()
            
            # Special handling for mode changes
            if field_name == "mode":
                if value == "Prompt":
                    section.resource_key = None
                else:  # Static
                    section.prompt = None
                    section.refs = []
            else:
                setattr(section, field_name, value)
            
            # Update radio choices to reflect new labels
            resource_choices = generate_resource_choices(current_state)
            section_choices = generate_section_choices(current_state)
            
            return (
                current_state,
                gr.update(choices=resource_choices),
                gr.update(choices=section_choices, value=current_state["selected_id"])
            )
        
        # Remove handler
        def handle_remove(current_state):
            """Remove selected item."""
            new_state = remove_selected(current_state)
            resource_choices, section_choices = update_lists(new_state)
            return [
                new_state,
                resource_choices,
                section_choices,
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(visible=False)
            ]
        
        # Validate handler
        def handle_validate(current_state):
            """Validate the outline."""
            is_valid, message = validate_outline_data(current_state["outline"])
            return gr.update(value=message, visible=True)
        
        # Download handler
        def handle_download(current_state):
            """Download outline as JSON."""
            outline_dict = current_state["outline"].to_dict()
            json_str = json.dumps(outline_dict, indent=2)
            # Save to a temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(json_str)
                return f.name
        
        # Upload handler
        def handle_upload(file, current_state):
            """Upload outline from JSON."""
            if file:
                # Gradio returns the file path as a string
                with open(file, 'r') as f:
                    content = f.read()
                data = json.loads(content)
                current_state["outline"] = Outline.from_dict(data)
                current_state["selected_id"] = None
                current_state["selected_type"] = None
                
                # Update UI
                resource_choices, section_choices = update_lists(current_state)
                
                return [
                    current_state,
                    current_state["outline"].title,
                    current_state["outline"].general_instruction,
                    resource_choices,
                    section_choices,
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(visible=False)
                ]
            return [current_state] + [gr.update()] * 7
        
        # Generate handler
        async def handle_generate(current_state):
            """Generate document from outline."""
            try:
                result = await generate_document(current_state["outline"])
                return {
                    output_container: gr.update(visible=True),
                    output_markdown: result["content"],
                    download_doc_btn: gr.update(
                        visible=True,
                        value=result["content"].encode(),
                        label=f"{current_state['outline'].title}.md"
                    )
                }
            except Exception as e:
                return {
                    output_container: gr.update(visible=True),
                    output_markdown: f"Error generating document: {str(e)}",
                    download_doc_btn: gr.update(visible=False)
                }
        
        # Preview handler
        def handle_preview(current_state):
            """Preview outline as JSON."""
            outline_dict = current_state["outline"].to_dict()
            json_str = json.dumps(outline_dict, indent=2)
            return {
                output_container: gr.update(visible=True),
                output_markdown: f"```json\n{json_str}\n```",
                download_doc_btn: gr.update(visible=False)
            }
        
        # Mode toggle for section editor
        def toggle_section_mode(mode):
            """Toggle between prompt and static mode."""
            is_prompt = mode == "Prompt"
            return {
                section_editor["prompt_container"]: gr.update(visible=is_prompt),
                section_editor["static_container"]: gr.update(visible=not is_prompt)
            }
        
        # Connect all handlers
        resource_add_btn.click(
            handle_add_resource,
            inputs=[state],
            outputs=[
                state, resource_radio, section_radio, empty_state,
                resource_editor["container"], section_editor["container"],
                resource_editor["key"], resource_editor["description"],
                resource_editor["path"], resource_editor["merge_mode"],
                section_editor["title"], section_editor["mode"],
                section_editor["prompt"], section_editor["refs"],
                section_editor["resource_key"]
            ]
        )
        
        section_add_btn.click(
            lambda s: handle_add_section(s, False),
            inputs=[state],
            outputs=[
                state, resource_radio, section_radio, empty_state,
                resource_editor["container"], section_editor["container"],
                resource_editor["key"], resource_editor["description"],
                resource_editor["path"], resource_editor["merge_mode"],
                section_editor["title"], section_editor["mode"],
                section_editor["prompt"], section_editor["refs"],
                section_editor["resource_key"]
            ]
        )
        
        section_sub_btn.click(
            lambda s: handle_add_section(s, True),
            inputs=[state],
            outputs=[
                state, resource_radio, section_radio, empty_state,
                resource_editor["container"], section_editor["container"],
                resource_editor["key"], resource_editor["description"],
                resource_editor["path"], resource_editor["merge_mode"],
                section_editor["title"], section_editor["mode"],
                section_editor["prompt"], section_editor["refs"],
                section_editor["resource_key"]
            ]
        )
        
        resource_remove_btn.click(
            handle_remove,
            inputs=[state],
            outputs=[state, resource_radio, section_radio, empty_state,
                    resource_editor["container"], section_editor["container"]]
        )
        
        section_remove_btn.click(
            handle_remove,
            inputs=[state],
            outputs=[state, resource_radio, section_radio, empty_state,
                    resource_editor["container"], section_editor["container"]]
        )
        
        # Auto-save resource fields
        resource_editor["key"].change(
            lambda v, s: auto_save_resource_field("key", v, s),
            inputs=[resource_editor["key"], state],
            outputs=[state, resource_radio, section_radio]
        )
        
        resource_editor["description"].change(
            lambda v, s: auto_save_resource_field("description", v, s),
            inputs=[resource_editor["description"], state],
            outputs=[state, resource_radio, section_radio]
        )
        
        resource_editor["path"].change(
            lambda v, s: auto_save_resource_field("path", v, s),
            inputs=[resource_editor["path"], state],
            outputs=[state, resource_radio, section_radio]
        )
        
        resource_editor["file"].change(
            lambda v, s: auto_save_resource_field("path", v, s) if v else (s, gr.update(), gr.update()),
            inputs=[resource_editor["file"], state],
            outputs=[state, resource_radio, section_radio]
        )
        
        resource_editor["merge_mode"].change(
            lambda v, s: auto_save_resource_field("merge_mode", v, s),
            inputs=[resource_editor["merge_mode"], state],
            outputs=[state, resource_radio, section_radio]
        )
        
        # Auto-save section fields
        section_editor["title"].change(
            lambda v, s: auto_save_section_field("title", v, s),
            inputs=[section_editor["title"], state],
            outputs=[state, resource_radio, section_radio]
        )
        
        # Connect both auto-save and toggle visibility for mode
        section_editor["mode"].change(
            lambda v, s: auto_save_section_field("mode", v, s),
            inputs=[section_editor["mode"], state],
            outputs=[state, resource_radio, section_radio]
        ).then(
            toggle_section_mode,
            inputs=[section_editor["mode"]],
            outputs=[section_editor["prompt_container"], 
                    section_editor["static_container"]]
        )
        
        section_editor["prompt"].change(
            lambda v, s: auto_save_section_field("prompt", v, s),
            inputs=[section_editor["prompt"], state],
            outputs=[state, resource_radio, section_radio]
        )
        
        section_editor["refs"].change(
            lambda v, s: auto_save_section_field("refs", v, s),
            inputs=[section_editor["refs"], state],
            outputs=[state, resource_radio, section_radio]
        )
        
        section_editor["resource_key"].change(
            lambda v, s: auto_save_section_field("resource_key", v, s),
            inputs=[section_editor["resource_key"], state],
            outputs=[state, resource_radio, section_radio]
        )
        
        validate_btn.click(
            handle_validate,
            inputs=[state],
            outputs=[validation_message]
        )
        
        download_btn.click(
            handle_download,
            inputs=[state],
            outputs=[gr.File()]
        )
        
        upload_btn.upload(
            handle_upload,
            inputs=[upload_btn, state],
            outputs=[state, title, instructions, resource_radio, section_radio,
                    empty_state, resource_editor["container"], section_editor["container"]]
        )
        
        generate_btn.click(
            handle_generate,
            inputs=[state],
            outputs=[output_container, output_markdown, download_doc_btn]
        )
        
        preview_btn.click(
            handle_preview,
            inputs=[state],
            outputs=[output_container, output_markdown, download_doc_btn]
        )
    
    return app