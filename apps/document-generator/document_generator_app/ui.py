"""
Simplified UI for Document Generator - all UI code in one module.
Following "ruthless simplicity" principle.
"""

import gradio as gr
import json
import os
import uuid
from typing import Dict, Any, List, Optional, Tuple

from .models.outline import Outline, Resource, Section, validate_outline
from .executor.runner import generate_document
from .package_handler import DocpackHandler


# ============================================================================
# State Management
# ============================================================================


def create_initial_state() -> Dict[str, Any]:
    """Create initial app state."""
    return {
        "outline": Outline(title="", general_instruction=""),
        "selected_type": None,  # "resource" or "section"
        "selected_id": None,  # e.g., "resource_0" or "section_1_2"
        "session_id": str(uuid.uuid4()),  # Unique session ID for this UI instance
    }


# ============================================================================
# Utility Functions
# ============================================================================


def validate_outline_data(outline: Outline) -> Tuple[bool, str]:
    """Validate an outline and return (is_valid, message)."""
    try:
        validate_outline(outline.to_dict())
        return True, "Outline is valid"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def get_section_at_path(sections: List[Section], path: List[int]) -> Optional[Section]:
    """Navigate to a section using a path of indices."""
    current = sections
    for i, idx in enumerate(path):
        if idx >= len(current):
            return None
        if i == len(path) - 1:
            return current[idx]
        current = current[idx].sections
    return None


def add_section_at_path(sections: List[Section], path: List[int], new_section: Section) -> None:
    """Add a section as a subsection at the given path."""
    if not path:
        sections.append(new_section)
        return

    parent = get_section_at_path(sections, path)
    if parent:
        if not hasattr(parent, "sections") or parent.sections is None:
            parent.sections = []
        parent.sections.append(new_section)


def remove_section_at_path(sections: List[Section], path: List[int]) -> None:
    """Remove a section at the given path."""
    if not path:
        return

    if len(path) == 1:
        if path[0] < len(sections):
            sections.pop(path[0])
    else:
        parent_path = path[:-1]
        parent = get_section_at_path(sections, parent_path)
        if parent and hasattr(parent, "sections") and parent.sections:
            if path[-1] < len(parent.sections):
                parent.sections.pop(path[-1])


# ============================================================================
# UI Component Creation
# ============================================================================


def create_resource_editor() -> Dict[str, Any]:
    """Create the resource editor form components."""
    with gr.Column(visible=False) as container:
        gr.Markdown("### Edit Resource")

        key = gr.Textbox(label="Key *", placeholder="unique_key")
        description = gr.TextArea(label="Description", placeholder="Describe what this resource contains...", lines=3)

        gr.Markdown("#### Resource Source")
        with gr.Tabs() as resource_source_tabs:
            with gr.TabItem("Upload File", id="upload_file"):
                bundled_file_info = gr.Markdown(visible=False)
                file = gr.File(label="Upload File", file_types=None)

            with gr.TabItem("URL", id="url_tab"):
                url = gr.Textbox(label="URL", placeholder="https://example.com/data.md")

    return {
        "container": container,
        "key": key,
        "description": description,
        "bundled_file_info": bundled_file_info,
        "file": file,
        "url": url,
        "resource_source_tabs": resource_source_tabs,
    }


def create_section_editor() -> Dict[str, Any]:
    """Create the section editor form components."""
    with gr.Column(visible=False) as container:
        gr.Markdown("### Edit Section")

        title = gr.Textbox(label="Title *", placeholder="Section Title")

        with gr.Tabs() as content_mode_tabs:
            with gr.TabItem("Prompt", id="prompt_mode") as prompt_tab:
                prompt = gr.TextArea(label="Prompt", placeholder="Instructions for generating this section...", lines=4)
                # Note: We'll populate choices dynamically
                refs = gr.Dropdown(label="Referenced Resources", choices=[], multiselect=True, interactive=True)

            with gr.TabItem("Static", id="static_mode") as static_tab:
                resource_key = gr.Dropdown(label="Resource Key", choices=[], interactive=True)

    return {
        "container": container,
        "title": title,
        "prompt": prompt,
        "refs": refs,
        "resource_key": resource_key,
        "content_mode_tabs": content_mode_tabs,
        "prompt_tab": prompt_tab,
        "static_tab": static_tab,
    }


# ============================================================================
# Choice Generation
# ============================================================================


def generate_resource_choices(state_data: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Generate choices for resource radio."""
    if not state_data or not state_data["outline"].resources:
        return []

    choices = []
    for i, res in enumerate(state_data["outline"].resources):
        label = res.key or f"Resource {i + 1}"
        value = f"resource_{i}"
        choices.append((label, value))
    return choices


def generate_section_choices(state_data: Dict[str, Any]) -> List[Tuple[str, str]]:
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
            # Use non-breaking spaces for indentation
            if level == 0:
                indent = ""
            elif level == 1:
                indent = "└─ "
            else:
                indent = "\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0" * (level - 1) + "└─ "

            section_label = sec.title or f"Section {'.'.join(map(str, current_path))}"
            label = f"{indent}{section_label}"
            value = f"section_{'_'.join(map(str, current_path))}"
            choices.append((label, value))

            # Add subsections
            if sec.sections and level < 3:
                add_sections(sec.sections, current_path, level + 1)

    add_sections(state_data["outline"].sections)
    return choices


# ============================================================================
# Validation and Preview
# ============================================================================


def validate_and_preview(state_data: Dict[str, Any]) -> Tuple[str, Any, Any, Any]:
    """Validate outline and update JSON preview."""
    if not state_data:
        return "", gr.update(visible=False), gr.update(interactive=False), gr.update(visible=False)

    try:
        outline_dict = state_data["outline"].to_dict()
        json_str = json.dumps(outline_dict, indent=2)

        is_valid, message = validate_outline_data(state_data["outline"])

        # Update download visibility
        has_content = state_data["outline"].title or state_data["outline"].resources or state_data["outline"].sections
        download_visible = gr.update(visible=has_content)

        if is_valid:
            return json_str, gr.update(visible=False), gr.update(interactive=True), download_visible
        else:
            return (
                json_str,
                gr.update(value=f"⚠️ {message}", visible=True),
                gr.update(interactive=False),
                download_visible,
            )
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        return "", gr.update(value=error_msg, visible=True), gr.update(interactive=False), gr.update(visible=False)


# ============================================================================
# State Update Functions
# ============================================================================


def select_item(item_id: str, item_type: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle clicking on a list item."""
    state["selected_id"] = item_id
    state["selected_type"] = item_type
    return state


def add_resource(state: Dict[str, Any]) -> Dict[str, Any]:
    """Add new resource and select it."""
    state["outline"].resources.append(Resource(key="", path="", description=""))
    state["selected_id"] = f"resource_{len(state['outline'].resources) - 1}"
    state["selected_type"] = "resource"
    return state


def add_section(state: Dict[str, Any], as_subsection: bool = False) -> Dict[str, Any]:
    """Add new section (top-level or as subsection of selected)."""
    new_section = Section(title="New Section", prompt="")
    new_section._mode = "Prompt"  # Default to prompt mode

    if as_subsection and state["selected_type"] == "section":
        # Add as subsection of selected section
        path_str = state["selected_id"].split("_")[1:]
        path = [int(p) for p in path_str]

        # Check if we're within depth limit (max 4 levels)
        if len(path) < 4:
            add_section_at_path(state["outline"].sections, path, new_section)
            # Update selection to the new subsection
            parent = get_section_at_path(state["outline"].sections, path)
            if parent and hasattr(parent, "sections") and parent.sections:
                new_idx = len(parent.sections) - 1
                state["selected_id"] = f"section_{'_'.join(path_str + [str(new_idx)])}"
    else:
        # Add at same level as selected section (or top-level if nothing selected)
        if state["selected_type"] == "section":
            path_str = state["selected_id"].split("_")[1:]
            path = [int(p) for p in path_str]

            if len(path) == 1:
                # Top-level section - insert after it
                insert_idx = path[0] + 1
                state["outline"].sections.insert(insert_idx, new_section)
                state["selected_id"] = f"section_{insert_idx}"
            else:
                # Nested section - insert after it at same level
                parent_path = path[:-1]
                parent = get_section_at_path(state["outline"].sections, parent_path)
                if parent and hasattr(parent, "sections"):
                    insert_idx = path[-1] + 1
                    parent.sections.insert(insert_idx, new_section)
                    state["selected_id"] = f"section_{'_'.join([str(p) for p in parent_path] + [str(insert_idx)])}"
        else:
            # No section selected - add to end of top-level
            state["outline"].sections.append(new_section)
            state["selected_id"] = f"section_{len(state['outline'].sections) - 1}"

    state["selected_type"] = "section"
    return state


def remove_selected(state: Dict[str, Any]) -> Dict[str, Any]:
    """Remove the selected item."""
    if not state["selected_id"]:
        return state

    if state["selected_type"] == "resource":
        idx = int(state["selected_id"].split("_")[1])
        if idx < len(state["outline"].resources):
            state["outline"].resources.pop(idx)

    elif state["selected_type"] == "section":
        path_str = state["selected_id"].split("_")[1:]
        path = [int(p) for p in path_str]
        remove_section_at_path(state["outline"].sections, path)

    # Clear selection
    state["selected_id"] = None
    state["selected_type"] = None
    return state


# ============================================================================
# Document Generation
# ============================================================================


def start_generation() -> List[Any]:
    """Show generation start state."""
    return [
        gr.update(value="🔄 Generating document...", interactive=False),  # generate_btn
        gr.update(value="⏳ Generating your document, please wait...", visible=True),  # generation_status
        gr.update(visible=False),  # output_container
        gr.update(visible=False),  # download_doc_btn
    ]


async def handle_generate(current_state: Dict[str, Any]) -> List[Any]:
    """Generate document from outline."""
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Starting document generation for outline: {current_state['outline'].title}")
        content = await generate_document(current_state["outline"], current_state.get("session_id"))
        logger.info(f"Generated content length: {len(content)}")

        # Check if content is suspiciously short (just header)
        lines = content.strip().split("\n")
        if len(lines) <= 3 and not any(len(line.strip()) > 50 for line in lines):
            error_msg = (
                f"⚠️ Document generation appears incomplete. Generated only {len(lines)} lines. Check logs for details."
            )
            logger.warning(error_msg)
            return [
                gr.update(value="Generate Document", interactive=True),  # generate_btn
                gr.update(value=error_msg, visible=True),  # generation_status
                gr.update(visible=True),  # output_container
                content
                + "\n\n---\n\n**Debug Info:**\n"
                + f"Content length: {len(content)} characters\nLines: {len(lines)}",  # output_markdown
                gr.update(visible=False),  # download_doc_btn
            ]

        # Save content to a temporary file for download
        filename = f"{current_state['outline'].title}.md" if current_state["outline"].title else "document.md"
        from .session import session_manager

        session_dir = session_manager.get_session_dir(current_state.get("session_id"))
        file_path = os.path.join(session_dir, filename)
        with open(file_path, "w") as f:
            f.write(content)

        return [
            gr.update(value="Generate Document", interactive=True),  # generate_btn
            gr.update(value="✅ Document generated successfully!", visible=True),  # generation_status
            gr.update(visible=True),  # output_container
            content,  # output_markdown
            gr.update(  # download_doc_btn
                visible=True, value=file_path, label=f"Download {filename}"
            ),
        ]
    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        logger.error(f"Document generation failed: {str(e)}")
        logger.error(f"Full traceback: {error_details}")

        return [
            gr.update(value="Generate Document", interactive=True),  # generate_btn
            gr.update(value=f"❌ Error: {str(e)}", visible=True),  # generation_status
            gr.update(visible=True),  # output_container
            f"Error generating document: {str(e)}\n\n---\n\n**Full Error Details:**\n```\n{error_details}\n```",  # output_markdown
            gr.update(visible=False),  # download_doc_btn
        ]


# ============================================================================
# Main UI Builder
# ============================================================================


def build_editor() -> gr.Blocks:
    """Create the main Gradio Blocks application."""

    # CSS for vertical radio buttons and section backgrounds
    custom_css = """
    .radio-vertical .wrap {
        flex-direction: column;
    }
    .section-block {
        background-color: var(--block-background-fill) !important;
        padding: 16px !important;
        margin: 8px 0 !important;
        border-radius: var(--block-radius) !important;
        border: 1px solid var(--block-border-color) !important;
    }
    .preview-block {
        padding: 16px !important;
        margin: 8px 0 !important;
        border-radius: var(--block-radius) !important;
        border: 1px solid var(--block-border-color) !important;
    }
    """

    with gr.Blocks(title="Document Generator", theme="soft", css=custom_css) as app:
        state = gr.State(create_initial_state())

        gr.Markdown("# Document Generator")
        gr.Markdown("Create structured documents with AI assistance")

        with gr.Row():
            # Left Column - Lists
            with gr.Column(scale=3, min_width=300):
                # Input options
                with gr.Tabs():
                    with gr.TabItem("Upload Docpack"):
                        upload_btn = gr.UploadButton("Upload Docpack", file_types=[".docpack"], variant="secondary")

                    with gr.TabItem("Examples"):
                        # Create dropdown choices from example outlines
                        from .config import settings

                        example_choices = [(ex.name, idx) for idx, ex in enumerate(settings.example_outlines)]
                        example_dropdown = gr.Dropdown(choices=example_choices, label="Example Outlines", type="index")
                        load_example_btn = gr.Button("Load Example", variant="secondary")

                # Document metadata
                title = gr.Textbox(label="Document Title", placeholder="Enter your document title...")
                instructions = gr.TextArea(
                    label="General Instructions", placeholder="Overall guidance for document generation...", lines=3
                )

                # Resources section
                with gr.Column(elem_classes="section-block"):
                    gr.Markdown("### Resources")
                    resource_radio = gr.Radio(
                        label=None,
                        choices=[],
                        container=False,
                        elem_id="resource_radio",
                        elem_classes=["radio-vertical"],
                    )
                    with gr.Row():
                        resource_add_btn = gr.Button("+ Add", size="sm")
                        resource_remove_btn = gr.Button("- Remove", size="sm")

                # Sections section
                with gr.Column(elem_classes="section-block"):
                    gr.Markdown("### Document Structure")
                    gr.Markdown(
                        "*Note: Changing resource keys may require re-selecting sections that reference them*",
                        elem_classes=["markdown-small"],
                    )
                    section_radio = gr.Radio(
                        label=None,
                        choices=[],
                        container=False,
                        elem_id="section_radio",
                        elem_classes=["radio-vertical"],
                    )

                    with gr.Row():
                        section_add_btn = gr.Button("+ Add", size="sm")
                        section_sub_btn = gr.Button("+ Sub", size="sm")
                        section_remove_btn = gr.Button("- Remove", size="sm")

            # Right Column - Editor
            with gr.Column(scale=2, min_width=300):
                # Empty state
                empty_state = gr.Markdown("### Select an item to edit", visible=True)

                # Editors
                resource_editor = create_resource_editor()
                section_editor = create_section_editor()

                # Validation message
                validation_message = gr.Markdown(visible=False)

                # Generation section
                gr.Markdown("---")
                generate_btn = gr.Button("Generate Document", variant="primary", interactive=False)
                generation_status = gr.Markdown(visible=False)

                download_doc_btn = gr.DownloadButton("Download Document", visible=False)

                # Download docpack section
                gr.Markdown("---")
                download_docpack_btn = gr.DownloadButton("Download Docpack", variant="secondary", visible=False)

                # Live JSON preview
                with gr.Accordion("Outline Preview (JSON)", open=False):
                    json_preview = gr.Code(
                        label="Current Outline Structure",
                        language="json",
                        interactive=False,
                        wrap_lines=True,
                        lines=20,
                    )

        # Output area
        output_container = gr.Column(visible=False, elem_classes="preview-block")
        with output_container:
            output_markdown = gr.Markdown()

        # ====================================================================
        # Event Handlers
        # ====================================================================

        def update_lists(state_data):
            """Update both radio lists based on state."""
            resource_choices = generate_resource_choices(state_data)
            section_choices = generate_section_choices(state_data)

            # Get current selection
            selected_value = None
            if state_data["selected_type"] == "resource":
                selected_value = state_data["selected_id"]

            return (
                gr.update(
                    choices=resource_choices,
                    value=selected_value if state_data["selected_type"] == "resource" else None,
                ),
                gr.update(
                    choices=section_choices,
                    value=state_data["selected_id"] if state_data["selected_type"] == "section" else None,
                ),
            )

        def handle_selection(selected_id, selected_type, current_state):
            """Handle radio selection and update editors."""
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
                    "",
                    "",
                    gr.update(visible=False),
                    "",
                    "",
                    "",
                    [],
                    "",
                    gr.update(selected="upload_file"),
                    gr.update(selected="prompt_mode"),
                ]

            # Update state
            new_state = select_item(selected_id, selected_type, current_state)

            # Update UI visibility
            show_resource = selected_type == "resource"
            show_section = selected_type == "section"

            # Default values
            res_key = ""
            res_desc = ""
            res_url = ""
            bundled_file_info = gr.update(visible=False)
            sec_title = ""
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
                    # Handle URL vs bundled file display
                    if res.path and res.path.startswith(("http://", "https://")):
                        res_url = res.path
                        bundled_file_info = gr.update(visible=False)
                    else:
                        res_url = ""  # Leave URL field empty for bundled files
                        if res.path:
                            # Check if file actually exists in session
                            from .session import session_manager

                            files_dir = session_manager.get_files_dir(new_state.get("session_id"))
                            file_path = files_dir / res.path

                            if file_path.exists():
                                bundled_file_info = gr.update(value=f"**Bundled File:** `{res.path}` ✓", visible=True)
                            else:
                                bundled_file_info = gr.update(
                                    value=f"**Referenced File:** `{res.path}` ⚠️ *File not uploaded*", visible=True
                                )
                        else:
                            bundled_file_info = gr.update(visible=False)

            # Determine which resource source tab should be selected
            # Check if path is a URL
            is_url = res_url.startswith(("http://", "https://")) if res_url else False
            resource_source_tab_selected = "url_tab" if show_resource and is_url else "upload_file"

            # Update section editor values and determine content mode tab
            sec = None
            content_mode_tab_selected = "prompt_mode"  # default
            if show_section:
                path = [int(p) for p in selected_id.split("_")[1:]]
                sec = get_section_at_path(new_state["outline"].sections, path)
                if sec:
                    sec_title = sec.title or ""
                    sec_prompt = sec.prompt or ""
                    # Filter out refs that no longer exist
                    valid_keys = [r.key for r in new_state["outline"].resources if r.key]
                    sec_refs = [ref for ref in (sec.refs or []) if ref in valid_keys]
                    sec_resource_key = sec.resource_key or ""

                    # Set mode based on current data if not already set
                    if not hasattr(sec, "_mode") or sec._mode is None:
                        sec._mode = "Static" if sec_resource_key and not sec_prompt else "Prompt"

                    # Determine which content mode tab should be selected based on section mode
                    content_mode_tab_selected = (
                        "static_mode" if getattr(sec, "_mode", None) == "Static" else "prompt_mode"
                    )

            # Update radio choices
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
                bundled_file_info,
                res_url,
                sec_title,
                sec_prompt,
                gr.update(
                    choices=[r.key for r in new_state["outline"].resources if r.key], value=sec_refs if sec_refs else []
                ),
                gr.update(
                    choices=[r.key for r in new_state["outline"].resources if r.key],
                    value=sec_resource_key
                    if sec_resource_key and sec_resource_key in [r.key for r in new_state["outline"].resources if r.key]
                    else None,
                ),
                gr.update(selected=resource_source_tab_selected),
                gr.update(selected=content_mode_tab_selected),
            ]

        def handle_resource_click(val, current_state):
            """Handle resource radio click without updating own radio."""
            if not val:
                return [current_state] + [gr.update()] * 15
            result = handle_selection(val, "resource", current_state)
            result[1] = gr.update()  # Don't update the resource radio itself
            return result

        def handle_section_click(val, current_state):
            """Handle section radio click without updating own radio."""
            if not val:
                return [current_state] + [gr.update()] * 15
            result = handle_selection(val, "section", current_state)
            result[2] = gr.update()  # Don't update the section radio itself
            return result

        def update_metadata(state_data, doc_title, doc_instructions):
            """Update document metadata in state."""
            if state_data:
                state_data["outline"].title = doc_title or ""
                state_data["outline"].general_instruction = doc_instructions or ""
            resource_choices, section_choices = update_lists(state_data)
            json_str, validation_msg, generate_btn_update, download_btn_update = validate_and_preview(state_data)
            return (
                state_data,
                resource_choices,
                section_choices,
                json_str,
                validation_msg,
                generate_btn_update,
                download_btn_update,
            )

        def handle_add_resource(current_state):
            """Add a new resource."""
            new_state = add_resource(current_state)
            return handle_selection(new_state["selected_id"], new_state["selected_type"], new_state)

        def handle_add_section(current_state, as_subsection=False):
            """Add a new section."""
            new_state = add_section(current_state, as_subsection)
            return handle_selection(new_state["selected_id"], new_state["selected_type"], new_state)

        def auto_save_resource_field(field_name, value, current_state):
            """Auto-save a resource field."""
            if not current_state["selected_id"] or current_state["selected_type"] != "resource":
                json_str, validation_msg, generate_btn_update, download_btn_update = validate_and_preview(current_state)
                return current_state, gr.update(), gr.update(), json_str, validation_msg, generate_btn_update

            # Get current resource data
            idx = int(current_state["selected_id"].split("_")[1])
            if idx >= len(current_state["outline"].resources):
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return current_state, gr.update(), gr.update(), json_str, validation_msg, generate_btn_update

            # Update the specific field
            resource = current_state["outline"].resources[idx]
            setattr(resource, field_name, value)

            # Update radio choices to reflect new labels
            resource_choices = generate_resource_choices(current_state)
            section_choices = generate_section_choices(current_state)

            # Validate and preview
            json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)

            # If changing a resource key, clear any section selection to avoid ref conflicts
            if field_name == "key":
                return (
                    current_state,
                    gr.update(choices=resource_choices, value=current_state["selected_id"]),
                    gr.update(choices=section_choices, value=None),
                    json_str,
                    validation_msg,
                    generate_btn_update,
                )

            return (
                current_state,
                gr.update(choices=resource_choices, value=current_state["selected_id"]),
                gr.update(choices=section_choices),
                json_str,
                validation_msg,
                generate_btn_update,
            )

        def auto_save_section_field(field_name, value, current_state):
            """Auto-save a section field."""
            if not current_state["selected_id"] or current_state["selected_type"] != "section":
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return current_state, gr.update(), gr.update(), json_str, validation_msg, generate_btn_update

            # Get current section
            path = [int(p) for p in current_state["selected_id"].split("_")[1:]]
            section = get_section_at_path(current_state["outline"].sections, path)

            if not section:
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return current_state, gr.update(), gr.update(), json_str, validation_msg, generate_btn_update

            # Set the field value
            setattr(section, field_name, value)

            # Only update mode if not explicitly set or if there's a clear indication
            if not hasattr(section, "_mode") or section._mode is None:
                # Auto-detect mode based on field values for new sections
                if hasattr(section, "resource_key") and hasattr(section, "prompt"):
                    if section.resource_key and not section.prompt:
                        section._mode = "Static"
                    else:
                        section._mode = "Prompt"

            # Update radio choices to reflect new labels
            resource_choices = generate_resource_choices(current_state)
            section_choices = generate_section_choices(current_state)

            # Validate and preview
            json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)

            return (
                current_state,
                gr.update(choices=resource_choices),
                gr.update(choices=section_choices, value=current_state["selected_id"]),
                json_str,
                validation_msg,
                generate_btn_update,
            )

        def handle_remove(current_state):
            """Remove selected item."""
            new_state = remove_selected(current_state)
            resource_choices, section_choices = update_lists(new_state)
            json_str, validation_msg, generate_btn_update, _ = validate_and_preview(new_state)
            return [
                new_state,
                resource_choices,
                section_choices,
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
                json_str,
                validation_msg,
                generate_btn_update,
            ]

        def handle_upload(file, current_state):
            """Upload docpack file."""
            if file:
                from pathlib import Path
                from .session import session_manager

                # Extract package to session directory
                session_dir = session_manager.get_session_dir(current_state.get("session_id"))
                package_path = Path(file)

                try:
                    outline_data, resource_files = DocpackHandler.extract_package(package_path, session_dir)
                    current_state["outline"] = Outline.from_dict(outline_data)
                    current_state["selected_id"] = None
                    current_state["selected_type"] = None

                    # Update UI
                    resource_choices, section_choices = update_lists(current_state)
                    json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)

                    return [
                        current_state,
                        current_state["outline"].title,
                        current_state["outline"].general_instruction,
                        resource_choices,
                        section_choices,
                        gr.update(visible=True),
                        gr.update(visible=False),
                        gr.update(visible=False),
                        json_str,
                        validation_msg,
                        generate_btn_update,
                    ]
                except Exception as e:
                    print(f"Error extracting docpack: {str(e)}")
                    return [current_state] + [gr.update()] * 10
            return [current_state] + [gr.update()] * 10

        def handle_load_example(example_idx, current_state):
            """Load an example docpack."""
            if example_idx is None:
                return [current_state] + [gr.update()] * 10

            try:
                from .config import settings
                from pathlib import Path
                from .session import session_manager

                # Get the example configuration
                example = settings.example_outlines[example_idx]

                # Get the directory where this module is located
                module_dir = Path(__file__).parent.parent
                example_path = module_dir / example.path

                # Extract docpack to session directory
                session_dir = session_manager.get_session_dir(current_state.get("session_id"))
                outline_data, resource_files = DocpackHandler.extract_package(example_path, session_dir)

                # Update state with loaded outline
                current_state["outline"] = Outline.from_dict(outline_data)
                current_state["selected_id"] = None
                current_state["selected_type"] = None

                # Update UI
                resource_choices, section_choices = update_lists(current_state)
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)

                return [
                    current_state,
                    current_state["outline"].title,
                    current_state["outline"].general_instruction,
                    resource_choices,
                    section_choices,
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(visible=False),
                    json_str,
                    validation_msg,
                    generate_btn_update,
                ]
            except Exception as e:
                # If loading fails, return current state with error
                print(f"Error loading example: {str(e)}")
                return [current_state] + [gr.update()] * 10

        def handle_file_change(file_path, current_state):
            """Handle file upload or deletion and manage session files directory."""
            if not current_state["selected_id"] or current_state["selected_type"] != "resource":
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return (
                    current_state,
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    json_str,
                    validation_msg,
                    generate_btn_update,
                )

            try:
                from pathlib import Path
                import shutil
                from .session import session_manager

                # Get current resource index
                idx = int(current_state["selected_id"].split("_")[1])
                if idx >= len(current_state["outline"].resources):
                    json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                    return (
                        current_state,
                        gr.update(),
                        gr.update(),
                        gr.update(),
                        json_str,
                        validation_msg,
                        generate_btn_update,
                    )

                resource = current_state["outline"].resources[idx]
                files_dir = session_manager.get_files_dir(current_state.get("session_id"))

                if file_path is None:
                    # File was cleared - delete the existing file and clear resource path
                    if resource.path and not resource.path.startswith(("http://", "https://")):
                        # Only delete if it's a file (not a URL)
                        old_file_path = files_dir / resource.path
                        if old_file_path.exists():
                            old_file_path.unlink()
                            print(f"Deleted file: {old_file_path}")

                    # Clear the resource path
                    resource.path = ""

                    # Update bundled file info to show nothing
                    bundled_file_info_update = gr.update(visible=False)

                else:
                    # File was uploaded - copy it and update resource
                    # First, clean up any existing file
                    if resource.path and not resource.path.startswith(("http://", "https://")):
                        old_file_path = files_dir / resource.path
                        if old_file_path.exists():
                            old_file_path.unlink()
                            print(f"Replaced file: {old_file_path}")

                    # Copy uploaded file to files directory
                    source_path = Path(file_path)
                    target_path = files_dir / source_path.name
                    shutil.copy2(source_path, target_path)

                    # Update resource with relative path (just filename)
                    resource.path = source_path.name

                    # Update bundled file info to show uploaded file
                    bundled_file_info_update = gr.update(
                        value=f"**Uploaded File:** `{source_path.name}` ✓", visible=True
                    )

                # Update radio choices to reflect changes
                resource_choices = generate_resource_choices(current_state)
                section_choices = generate_section_choices(current_state)

                # Validate and preview
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)

                return (
                    current_state,
                    gr.update(choices=resource_choices, value=current_state["selected_id"]),
                    gr.update(choices=section_choices),
                    bundled_file_info_update,
                    json_str,
                    validation_msg,
                    generate_btn_update,
                )

            except Exception as e:
                print(f"Error handling file change: {str(e)}")
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return (
                    current_state,
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    json_str,
                    validation_msg,
                    generate_btn_update,
                )

        def handle_download_docpack(current_state):
            """Create and download a docpack file."""
            try:
                from .session import session_manager

                session_dir = session_manager.get_session_dir(current_state.get("session_id"))
                files_dir = session_manager.get_files_dir(current_state.get("session_id"))

                # Get current outline data
                outline_data = current_state["outline"].to_dict()

                # Find resource files in session files directory
                resource_files = []
                for resource in current_state["outline"].resources:
                    if resource.path and not resource.path.startswith(("http://", "https://")):
                        # Only include uploaded files (not URLs)
                        resource_path = files_dir / resource.path
                        if resource_path.exists():
                            resource_files.append(resource_path)

                # Create docpack filename
                title = current_state["outline"].title or "outline"
                # Sanitize filename
                safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).rstrip()
                filename = f"{safe_title}.docpack"

                # Create docpack in session directory
                docpack_path = session_dir / filename
                DocpackHandler.create_package(outline_data, resource_files, docpack_path)

                return gr.update(value=str(docpack_path), label=f"Download {filename}")

            except Exception as e:
                print(f"Error creating docpack: {str(e)}")
                return gr.update()

        # ====================================================================
        # Connect Event Handlers
        # ====================================================================

        # Radio selections
        resource_radio.change(
            handle_resource_click,
            inputs=[resource_radio, state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                resource_editor["key"],
                resource_editor["description"],
                resource_editor["bundled_file_info"],
                resource_editor["url"],
                section_editor["title"],
                section_editor["prompt"],
                section_editor["refs"],
                section_editor["resource_key"],
                resource_editor["resource_source_tabs"],
                section_editor["content_mode_tabs"],
            ],
        )

        section_radio.change(
            handle_section_click,
            inputs=[section_radio, state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                resource_editor["key"],
                resource_editor["description"],
                resource_editor["bundled_file_info"],
                resource_editor["url"],
                section_editor["title"],
                section_editor["prompt"],
                section_editor["refs"],
                section_editor["resource_key"],
                resource_editor["resource_source_tabs"],
                section_editor["content_mode_tabs"],
            ],
        )

        # Metadata updates
        title.change(
            update_metadata,
            inputs=[state, title, instructions],
            outputs=[
                state,
                resource_radio,
                section_radio,
                json_preview,
                validation_message,
                generate_btn,
                download_docpack_btn,
            ],
        )

        instructions.change(
            update_metadata,
            inputs=[state, title, instructions],
            outputs=[
                state,
                resource_radio,
                section_radio,
                json_preview,
                validation_message,
                generate_btn,
                download_docpack_btn,
            ],
        )

        # Add/Remove buttons
        resource_add_btn.click(
            handle_add_resource,
            inputs=[state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                resource_editor["key"],
                resource_editor["description"],
                resource_editor["bundled_file_info"],
                resource_editor["url"],
                section_editor["title"],
                section_editor["prompt"],
                section_editor["refs"],
                section_editor["resource_key"],
                resource_editor["resource_source_tabs"],
                section_editor["content_mode_tabs"],
            ],
        )

        section_add_btn.click(
            lambda s: handle_add_section(s, False),
            inputs=[state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                resource_editor["key"],
                resource_editor["description"],
                resource_editor["bundled_file_info"],
                resource_editor["url"],
                section_editor["title"],
                section_editor["prompt"],
                section_editor["refs"],
                section_editor["resource_key"],
                resource_editor["resource_source_tabs"],
                section_editor["content_mode_tabs"],
            ],
        )

        section_sub_btn.click(
            lambda s: handle_add_section(s, True),
            inputs=[state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                resource_editor["key"],
                resource_editor["description"],
                resource_editor["bundled_file_info"],
                resource_editor["url"],
                section_editor["title"],
                section_editor["prompt"],
                section_editor["refs"],
                section_editor["resource_key"],
                resource_editor["resource_source_tabs"],
                section_editor["content_mode_tabs"],
            ],
        )

        resource_remove_btn.click(
            handle_remove,
            inputs=[state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                json_preview,
                validation_message,
                generate_btn,
            ],
        )

        section_remove_btn.click(
            handle_remove,
            inputs=[state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                json_preview,
                validation_message,
                generate_btn,
            ],
        )

        # Auto-save resource fields
        resource_editor["key"].change(
            lambda v, s: auto_save_resource_field("key", v, s),
            inputs=[resource_editor["key"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        )

        resource_editor["description"].change(
            lambda v, s: auto_save_resource_field("description", v, s),
            inputs=[resource_editor["description"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        )

        resource_editor["url"].change(
            lambda v, s: auto_save_resource_field("path", v, s),
            inputs=[resource_editor["url"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        )

        resource_editor["file"].change(
            handle_file_change,
            inputs=[resource_editor["file"], state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                resource_editor["bundled_file_info"],
                json_preview,
                validation_message,
                generate_btn,
            ],
        )

        # Auto-save section fields
        section_editor["title"].change(
            lambda v, s: auto_save_section_field("title", v, s),
            inputs=[section_editor["title"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        )

        section_editor["prompt"].change(
            lambda v, s: auto_save_section_field("prompt", v, s),
            inputs=[section_editor["prompt"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        )

        section_editor["refs"].change(
            lambda v, s: auto_save_section_field("refs", v, s),
            inputs=[section_editor["refs"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        )

        section_editor["resource_key"].change(
            lambda v, s: auto_save_section_field("resource_key", v, s),
            inputs=[section_editor["resource_key"], state],
            outputs=[state, resource_radio, section_radio, json_preview, validation_message, generate_btn],
        )

        # Handle content mode tab changes via individual tab events
        def handle_prompt_tab_select(current_state):
            """Handle switching to prompt mode tab."""
            if not current_state["selected_id"] or current_state["selected_type"] != "section":
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return (
                    current_state,
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    json_str,
                    validation_msg,
                    generate_btn_update,
                )

            # Get current section
            path = [int(p) for p in current_state["selected_id"].split("_")[1:]]
            section = get_section_at_path(current_state["outline"].sections, path)

            if not section:
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return (
                    current_state,
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    json_str,
                    validation_msg,
                    generate_btn_update,
                )

            # Set prompt mode (but keep all field values)
            section._mode = "Prompt"
            # Ensure prompt fields exist
            if not section.prompt:
                section.prompt = ""

            # Update UI (don't clear fields, just update choices and JSON)
            resource_choices = generate_resource_choices(current_state)
            section_choices = generate_section_choices(current_state)
            json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)

            return (
                current_state,
                gr.update(choices=resource_choices),
                gr.update(choices=section_choices, value=current_state["selected_id"]),
                gr.update(),  # Keep current resource_key value (don't change UI)
                json_str,
                validation_msg,
                generate_btn_update,
            )

        def handle_static_tab_select(current_state):
            """Handle switching to static mode tab."""
            if not current_state["selected_id"] or current_state["selected_type"] != "section":
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return (
                    current_state,
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    json_str,
                    validation_msg,
                    generate_btn_update,
                )

            # Get current section
            path = [int(p) for p in current_state["selected_id"].split("_")[1:]]
            section = get_section_at_path(current_state["outline"].sections, path)

            if not section:
                json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)
                return (
                    current_state,
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    json_str,
                    validation_msg,
                    generate_btn_update,
                )

            # Set static mode (but keep all field values)
            section._mode = "Static"
            # Set to first available resource if no resource is selected
            if not section.resource_key and current_state["outline"].resources:
                available_resources = [r.key for r in current_state["outline"].resources if r.key]
                if available_resources:
                    section.resource_key = available_resources[0]

            # Update UI (don't clear fields, just update choices and JSON)
            resource_choices = generate_resource_choices(current_state)
            section_choices = generate_section_choices(current_state)
            json_str, validation_msg, generate_btn_update, _ = validate_and_preview(current_state)

            return (
                current_state,
                gr.update(choices=resource_choices),
                gr.update(choices=section_choices, value=current_state["selected_id"]),
                gr.update(),  # Keep current prompt value (don't change UI)
                gr.update(),  # Keep current refs value (don't change UI)
                json_str,
                validation_msg,
                generate_btn_update,
            )

        # Upload handler
        upload_btn.upload(
            handle_upload,
            inputs=[upload_btn, state],
            outputs=[
                state,
                title,
                instructions,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                json_preview,
                validation_message,
                generate_btn,
            ],
        )

        # Example load handler
        load_example_btn.click(
            handle_load_example,
            inputs=[example_dropdown, state],
            outputs=[
                state,
                title,
                instructions,
                resource_radio,
                section_radio,
                empty_state,
                resource_editor["container"],
                section_editor["container"],
                json_preview,
                validation_message,
                generate_btn,
            ],
        )

        # Generate handler
        generate_btn.click(
            start_generation, outputs=[generate_btn, generation_status, output_container, download_doc_btn]
        ).then(
            handle_generate,
            inputs=[state],
            outputs=[generate_btn, generation_status, output_container, output_markdown, download_doc_btn],
        )

        # Tab change handlers for content mode
        section_editor["prompt_tab"].select(
            handle_prompt_tab_select,
            inputs=[state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                section_editor["resource_key"],
                json_preview,
                validation_message,
                generate_btn,
            ],
        )

        section_editor["static_tab"].select(
            handle_static_tab_select,
            inputs=[state],
            outputs=[
                state,
                resource_radio,
                section_radio,
                section_editor["prompt"],
                section_editor["refs"],
                json_preview,
                validation_message,
                generate_btn,
            ],
        )

        # Set up download docpack handler to update with file path when clicked
        download_docpack_btn.click(handle_download_docpack, inputs=[state], outputs=[download_docpack_btn])

        # Initial validation on load
        app.load(
            lambda s: validate_and_preview(s),
            inputs=[state],
            outputs=[json_preview, validation_message, generate_btn, download_docpack_btn],
        )

    return app
