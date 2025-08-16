# apps/document-generator/document_generator_app

[collect-files]

**Search:** ['apps/document-generator/document_generator_app']
**Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output', '.DS_Store', '*.DS_Store']
**Include:** []
**Date:** 8/15/2025, 3:42:41 PM
**Files:** 14

=== File: apps/document-generator/document_generator_app/__init__.py ===
"""Document Generator - Gradio app for generating documents with an enhanced interface"""

__version__ = "0.2.0"


=== File: apps/document-generator/document_generator_app/app.py ===
import argparse
import asyncio
import json
import os
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List

import gradio as gr
import pypandoc
from docx import Document
from docpack_file import DocpackHandler
from dotenv import load_dotenv

from .executor.runner import generate_docpack_from_prompt, generate_document
from .models.outline import Outline, Resource, Section
from .session import session_manager

# Load environment variables from .env file
load_dotenv()

# Global variable to track if app is running in dev mode
IS_DEV_MODE = False

# Supported file types for uploads
SUPPORTED_FILE_TYPES = [
    ".txt", ".md", ".py", ".c", ".cpp", ".h", ".java", ".js", ".ts", ".jsx", ".tsx",
    ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".sh", ".bash",
    ".zsh", ".fish", ".ps1", ".bat", ".cmd", ".rs", ".go", ".rb", ".php", ".pl", ".lua",
    ".r", ".m", ".swift", ".kt", ".scala", ".clj", ".ex", ".exs", ".elm", ".fs", ".ml",
    ".sql", ".html", ".htm", ".css", ".scss", ".sass", ".less", ".vue", ".svelte", ".astro",
    ".tex", ".rst", ".adoc", ".org", ".csv", ".docx"
]


def markdown_to_docx(markdown_content: str, output_path: str) -> str:
    """Convert markdown content to docx file and return the output path."""
    try:
        pypandoc.convert_text(
            markdown_content, 
            'docx', 
            format='md',
            outputfile=output_path,
            extra_args=['--extract-media=.']  # Extract images to current directory
        )
        return output_path
    except Exception as e:
        raise Exception(f"Failed to convert markdown to docx: {str(e)}")


def check_docx_protected(docx_path: str) -> tuple[bool, str]:
    """Check if a docx file is protected/encrypted without fully extracting text.
    Returns (is_protected, error_message)
    """
    try:
        from docx import Document
        filename = os.path.basename(docx_path)
        # Try to open the document
        doc = Document(docx_path)
        # Try to access at least one paragraph to ensure it's readable
        _ = len(doc.paragraphs)
        return False, ""
    except Exception as e:
        error_msg = str(e).lower()
        filename = os.path.basename(docx_path)
        # Check for common security/encryption error messages
        if any(term in error_msg for term in ['package not found']):
            return True, (
                f"Document '{filename}' appears to be protected or encrypted and cannot be processed."
            )
        else:
            # Some other error, but not protection-related
            return False, f"Document '{filename}' may have issues: {str(e)}"


def docx_to_text(docx_path: str) -> str:
    """Extract text content from a docx file."""
    try:
        doc = Document(docx_path)
        paragraphs = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():  # Only add non-empty paragraphs
                paragraphs.append(paragraph.text.strip())
        
        return '\n\n'.join(paragraphs)
    except Exception as e:
        error_msg = str(e).lower()
        filename = os.path.basename(docx_path)
        # Check for common security/encryption error messages
        if any(term in error_msg for term in ['package not found']):
            raise Exception(
                f"Document '{filename}' may be protected or encrypted and cannot be processed."
            )
        else:
            raise Exception(f"Failed to extract text from '{filename}': {str(e)}")



def json_to_outline(json_data: Dict[str, Any]) -> Outline:
    """Convert JSON structure to Outline dataclasses."""
    # Create outline with basic metadata
    outline = Outline(title=json_data.get("title", ""), general_instruction=json_data.get("general_instruction", ""))

    # Convert resources
    for res_data in json_data.get("resources", []):
        # Handle backward compatibility - use filename as title if title not present
        title = res_data.get("title", "")
        if not title:
            # Extract filename from path as default title
            title = os.path.basename(res_data["path"])

        resource = Resource(
            key=res_data["key"],
            path=res_data["path"],
            title=title,
            description=res_data["description"],
            merge_mode="concat",  # Default merge mode
        )
        outline.resources.append(resource)

    # Helper function to convert sections recursively
    def convert_sections(sections_data: List[Dict[str, Any]]) -> List[Section]:
        sections = []
        for sec_data in sections_data:
            section = Section(title=sec_data.get("title", ""))

            # Check if it has prompt (AI block) or resource_key (text block)
            if "prompt" in sec_data:
                # AI block
                section.prompt = sec_data["prompt"]
                section.refs = sec_data.get("refs", [])
                section._mode = None  # Default mode
            elif "resource_key" in sec_data:
                # Text block
                section.resource_key = sec_data["resource_key"]
                section._mode = "Static"

            # Convert nested sections
            if "sections" in sec_data:
                section.sections = convert_sections(sec_data["sections"])

            sections.append(section)

        return sections

    # Convert top-level sections
    outline.sections = convert_sections(json_data.get("sections", []))

    return outline


def add_ai_block(blocks, focused_block_id=None):
    """Add an AI content block."""
    new_block = {
        "id": str(uuid.uuid4()),
        "type": "ai",
        "heading": "",
        "content": "",
        "resources": [],
        "collapsed": True,  # Start collapsed
        "indent_level": 0,
    }

    # If no focused block or focused block not found, add at the end
    if not focused_block_id:
        return blocks + [new_block]

    # Find the focused block and insert after it
    for i, block in enumerate(blocks):
        if block["id"] == focused_block_id:
            # Inherit the indent level from the focused block
            new_block["indent_level"] = block.get("indent_level", 0)
            # Insert after the focused block
            return blocks[: i + 1] + [new_block] + blocks[i + 1 :]

    # If focused block not found, add at the end
    return blocks + [new_block]


def add_heading_block(blocks):
    """Add a heading block."""
    new_block = {"id": str(uuid.uuid4()), "type": "heading", "content": "Heading"}
    return blocks + [new_block]


def add_text_block(blocks, focused_block_id=None):
    """Add a text block."""
    new_block = {
        "id": str(uuid.uuid4()),
        "type": "text",
        "heading": "",
        "content": "",
        "resources": [],
        "collapsed": True,  # Start collapsed
        "indent_level": 0,
    }

    # If no focused block or focused block not found, add at the end
    if not focused_block_id:
        return blocks + [new_block]

    # Find the focused block and insert after it
    for i, block in enumerate(blocks):
        if block["id"] == focused_block_id:
            # Inherit the indent level from the focused block
            new_block["indent_level"] = block.get("indent_level", 0)
            # Insert after the focused block
            return blocks[: i + 1] + [new_block] + blocks[i + 1 :]

    # If focused block not found, add at the end
    return blocks + [new_block]


def delete_block(blocks, block_id, title, description, resources):
    """Delete a block by its ID and regenerate outline."""
    blocks = [block for block in blocks if block["id"] != block_id]

    # Regenerate outline and JSON
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return blocks, outline, json_str


def update_block_content(blocks, block_id, content, title, description, resources):
    """Update the content of a specific block and regenerate outline."""
    for block in blocks:
        if block["id"] == block_id:
            block["content"] = content
            # Also save to type-specific field
            if block["type"] == "ai":
                block["ai_content"] = content
            elif block["type"] == "text":
                block["text_content"] = content
                # Mark text block as edited when content changes
                if content:
                    block["edited"] = True
                    # Store original resource reference if exists
                    if "resources" in block and block["resources"]:
                        block["original_resource"] = block["resources"][0]
                        block["resources"] = []  # Clear resources since content is now edited
            break

    # Regenerate outline and JSON
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return blocks, outline, json_str


def update_block_heading(blocks, block_id, heading, title, description, resources):
    """Update the heading of a specific block and regenerate outline."""
    for block in blocks:
        if block["id"] == block_id:
            block["heading"] = heading
            break

    # Regenerate outline and JSON
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return blocks, outline, json_str


def set_focused_block(block_id):
    """Set the currently focused block."""
    return block_id


def reset_document(session_id=None):
    """Reset the document to initial empty state."""
    # Create new session ID
    new_session_id = str(uuid.uuid4())

    # Reset to initial blocks
    initial_blocks = [
        {
            "id": str(uuid.uuid4()),
            "type": "ai",
            "heading": "",
            "content": "",
            "resources": [],
            "collapsed": False,  # AI block starts expanded
            "indent_level": 0,
        },
        {
            "id": str(uuid.uuid4()),
            "type": "text",
            "heading": "",
            "content": "",
            "resources": [],
            "collapsed": True,  # Text block starts collapsed
            "indent_level": 0,
        },
    ]

    # Generate initial outline
    outline, json_str = regenerate_outline_from_state("", "", [], initial_blocks)

    # Return empty title, description, empty resources, initial blocks
    return (
        gr.update(value=""),  # title - use gr.update to ensure proper clearing
        gr.update(value=""),  # description - use gr.update to ensure proper clearing
        [],  # resources
        initial_blocks,  # blocks
        outline,  # outline
        json_str,  # json_output
        None,  # import_file
        new_session_id,  # session_id
        gr.update(
            value="<em>Click '▷ Generate' to see the generated content here.</em><br><br><br>", visible=True
        ),  # generated_content_html
        gr.update(visible=False),  # generated_content
        gr.update(interactive=False),  # save_doc_btn
    )


def convert_block_type(blocks, block_id, to_type, title, description, resources):
    """Convert a block from one type to another while preserving separate content for each type."""
    for block in blocks:
        if block["id"] == block_id:
            current_type = block["type"]

            # Save current content to type-specific field
            if current_type == "ai":
                block["ai_content"] = block.get("content", "")
                block["ai_resources"] = block.get("resources", [])
            elif current_type == "text":
                block["text_content"] = block.get("content", "")
                block["text_resources"] = block.get("resources", [])

            # Switch to new type
            block["type"] = to_type

            # Load content for the new type
            if to_type == "ai":
                block["content"] = block.get("ai_content", "")
                block["resources"] = block.get("ai_resources", [])
            elif to_type == "text":
                block["content"] = block.get("text_content", "")
                block["resources"] = block.get("text_resources", [])

            # Ensure all required fields exist
            if "heading" not in block:
                block["heading"] = ""
            if "collapsed" not in block:
                block["collapsed"] = False
            if "indent_level" not in block:
                block["indent_level"] = 0
            break

    # Regenerate outline and JSON
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return blocks, outline, json_str


def toggle_block_collapse(blocks, block_id):
    """Toggle the collapsed state of a specific block."""
    for block in blocks:
        if block["id"] == block_id:
            # Simply toggle the collapsed state
            block["collapsed"] = not block.get("collapsed", False)
            break
    return blocks


def update_block_indent(blocks, block_id, direction, title, description, resources):
    """Update the indent level of a specific block and regenerate outline."""
    # Find the index of the block being modified
    block_index = None
    for i, block in enumerate(blocks):
        if block["id"] == block_id:
            block_index = i
            break

    if block_index is None:
        outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
        return blocks, outline, json_str

    block = blocks[block_index]
    current_level = block.get("indent_level", 0)

    if direction == "in":
        # Check if this is the first block - if so, can't indent at all
        if block_index == 0:
            outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
            return blocks, outline, json_str

        # Get the previous block's indent level
        prev_block = blocks[block_index - 1]
        prev_level = prev_block.get("indent_level", 0)
        max_allowed_level = prev_level + 1

        # Can only indent if current level is less than max allowed and less than 5
        if current_level < max_allowed_level and current_level < 5:
            block["indent_level"] = current_level + 1
    elif direction == "out" and current_level > 0:
        block["indent_level"] = current_level - 1

    # Regenerate outline and JSON
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return blocks, outline, json_str


def save_inline_resources(blocks, output_dir):
    """Save inline resources from edited text blocks to disk."""
    saved_resources = []
    for block in blocks:
        if block.get("type") == "text" and block.get("edited") and block.get("text_content"):
            # Save the inline resource
            filename = f"inline_{block['id']}.txt"
            filepath = Path(output_dir) / filename
            filepath.write_text(block["text_content"], encoding="utf-8")
            saved_resources.append({"block_id": block["id"], "path": str(filepath)})
    return saved_resources


async def handle_document_generation(title, description, resources, blocks, session_id=None):
    """Generate document using the recipe executor."""
    json_str = ""  # Initialize json_str before the try block
    try:
        # Get or create session ID
        if not session_id:
            session_id = str(uuid.uuid4())

        # Use session temp directory for inline resources and output
        temp_dir = session_manager.get_temp_dir(session_id)

        # Generate the JSON with inline resources saved to temp directory
        json_str = generate_document_json(title, description, resources, blocks, save_inline=True, inline_dir=temp_dir)
        json_data = json.loads(json_str)

        # Remove is_inline flags for compatibility with json_to_outline
        for res in json_data.get("resources", []):
            if "is_inline" in res:
                del res["is_inline"]

        # Convert to Outline
        outline = json_to_outline(json_data)

        # Generate the document
        generated_content = await generate_document(outline, session_id, IS_DEV_MODE)

        # Save markdown to temporary file for download as docx
        docx_filename = f"{title}.docx" if title else "document.docx"
        docx_file_path = os.path.join(temp_dir, docx_filename)
        
        # Convert markdown to docx
        markdown_to_docx(generated_content, docx_file_path)

        return json_str, generated_content, docx_file_path, docx_filename

    except Exception as e:
        error_msg = f"Error generating document: {str(e)}"
        return json_str, error_msg, None, None


def generate_document_json(title, description, resources, blocks, save_inline=False, inline_dir=None):
    """Generate JSON structure from document data following the example format.

    Args:
        save_inline: If True, save inline resources to inline_dir and use real paths
        inline_dir: Directory to save inline resources to (required if save_inline=True)
    """
    import json

    # Create the base structure
    doc_json = {"title": title, "general_instruction": description, "resources": [], "sections": []}

    # Track inline resources that need to be added
    inline_resources = []

    # Process resources with their descriptions from the resources list
    for idx, resource in enumerate(resources):
        # Get description directly from the resource
        description = resource.get("description", "")
        # Get title from resource or default to filename
        title = resource.get("title", resource.get("name", os.path.basename(resource["path"])))
        doc_json["resources"].append({
            "key": f"resource_{idx + 1}",
            "path": resource["path"],
            "title": title,
            "description": description,
        })

    # Helper function to build nested sections based on indentation
    def build_nested_sections(blocks, start_idx=0, parent_level=-1):
        sections = []
        i = start_idx

        while i < len(blocks):
            block = blocks[i]
            current_level = block.get("indent_level", 0)

            # If this block is at a lower level than parent, return
            if current_level <= parent_level:
                break

            # If this block is at the expected level
            if current_level == parent_level + 1:
                if block["type"] in ["ai", "text"] and (
                    block.get("heading") or block.get("content") or block.get("resources")
                ):
                    section = {"title": block.get("heading", "Untitled Section")}

                    # Handle AI blocks vs Text blocks differently
                    if block["type"] == "ai":
                        # AI blocks always have these keys
                        section["prompt"] = block.get("content", "")
                        section["sections"] = []  # Will be populated if there are nested sections

                        # Handle refs - always include the key
                        refs = []
                        block_resources = block.get("resources", [])
                        if block_resources:
                            # Find the resource keys for this block's resources
                            for block_resource in block_resources:
                                # Find matching resource in the global resources list
                                for idx, resource in enumerate(resources):
                                    if resource["path"] == block_resource.get("path"):
                                        refs.append(f"resource_{idx + 1}")
                                        break
                        section["refs"] = refs

                    else:  # block['type'] == 'text'
                        # Text blocks always have these keys
                        section["resource_key"] = ""  # Default to empty string
                        section["sections"] = []  # Will be populated if there are nested sections

                        # Check if this text block has been edited
                        if block.get("edited") and block.get("text_content"):
                            # Create an inline resource for the edited content
                            inline_resource_key = f"inline_resource_{len(inline_resources) + 1}"
                            inline_resources.append({
                                "key": inline_resource_key,
                                "content": block["text_content"],
                                "block_id": block["id"],
                            })
                            section["resource_key"] = inline_resource_key
                        else:
                            # Handle regular file resource
                            block_resources = block.get("resources", [])
                            if block_resources:
                                # For text blocks, just use the first resource as resource_key
                                for block_resource in block_resources:
                                    # Find matching resource in the global resources list
                                    for idx, resource in enumerate(resources):
                                        if resource["path"] == block_resource.get("path"):
                                            section["resource_key"] = f"resource_{idx + 1}"
                                            break
                                    break  # Only use first resource for resource_key

                    # Check if next blocks are indented under this one
                    next_idx = i + 1
                    if next_idx < len(blocks) and blocks[next_idx].get("indent_level", 0) > current_level:
                        # Build subsections
                        subsections, next_idx = build_nested_sections(blocks, next_idx, current_level)
                        if subsections:
                            section["sections"] = subsections
                        i = next_idx - 1  # Adjust because we'll increment at the end

                    sections.append(section)

            i += 1

        return sections, i

    # Build the sections hierarchy
    doc_json["sections"], _ = build_nested_sections(blocks, 0, -1)

    # Add inline resources to the resources list
    if save_inline and inline_dir:
        # Actually save the inline resources and use real paths
        for inline_res in inline_resources:
            filename = f"inline_{inline_res['block_id']}.txt"
            filepath = Path(inline_dir) / filename
            filepath.write_text(inline_res["content"], encoding="utf-8")

            doc_json["resources"].append({
                "key": inline_res["key"],
                "path": str(filepath),
                "title": filename,  # Use filename as title for inline resources
                "description": "",  # No description for inline resources
                "is_inline": True,  # Mark as inline resource
            })
    else:
        # For preview, save to temp gradio directory immediately
        import tempfile

        gradio_temp_dir = Path(tempfile.gettempdir()) / "gradio"
        gradio_temp_dir.mkdir(exist_ok=True)

        for inline_res in inline_resources:
            # Generate unique filename with timestamp
            import time

            timestamp = str(int(time.time() * 1000000))
            filename = f"inline_{inline_res['block_id']}_{timestamp}.txt"
            filepath = gradio_temp_dir / filename
            filepath.write_text(inline_res["content"], encoding="utf-8")

            doc_json["resources"].append({
                "key": inline_res["key"],
                "path": str(filepath),
                "title": filename,  # Use filename as title for inline resources
                "description": "",  # No description for inline resources
                "is_inline": True,  # Mark as inline resource
            })

    return json.dumps(doc_json, indent=2)


def regenerate_outline_from_state(title, description, resources, blocks):
    """Regenerate the outline whenever any component changes."""
    try:
        json_str = generate_document_json(title, description, resources, blocks)
        json_data = json.loads(json_str)
        outline = json_to_outline(json_data)

        # Update global state whenever outline is regenerated
        global current_document_state
        current_document_state = {"title": title, "outline_json": json_str, "blocks": blocks}
        print(f"DEBUG: regenerate_outline_from_state called with title='{title}'")
        print(f"DEBUG: Updated global current_document_state: {current_document_state}")

        return outline, json_str
    except Exception as e:
        # Return None outline and error message in JSON
        import traceback

        print(f"ERROR in regenerate_outline_from_state: {str(e)}")
        print(traceback.format_exc())
        error_json = json.dumps({"error": str(e), "traceback": traceback.format_exc()}, indent=2)
        return None, error_json


def update_document_metadata(title, description, resources, blocks):
    """Update document title/description and regenerate outline."""
    # Just regenerate the outline with new metadata
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return outline, json_str


def update_block_resources(blocks, block_id, resource_json, title, description, resources):
    """Update a block's resources when a resource is dropped on it."""
    import json

    # Parse the resource data
    resource_data = json.loads(resource_json)

    # Find the block and update its resources
    for block in blocks:
        if block["id"] == block_id:
            if "resources" not in block:
                block["resources"] = []

            # For text blocks, only allow one resource AND auto-load content
            if block["type"] == "text":
                # Replace any existing resource
                block["resources"] = [resource_data]

                # Auto-load the file content into the text block
                try:
                    file_path = resource_data["path"]
                    if file_path.lower().endswith('.docx'):
                        # Extract text from docx file
                        block["content"] = docx_to_text(file_path)
                    else:
                        # Read as regular text file
                        with open(file_path, "r", encoding="utf-8") as f:
                            block["content"] = f.read()
                except Exception as e:
                    print(f"Error loading file content: {e}")
                    # Keep existing content if file can't be read
            else:
                # For AI blocks, allow multiple resources
                # Check if resource already exists in the block
                exists = False
                for res in block["resources"]:
                    if res.get("path") == resource_data.get("path"):
                        exists = True
                        break

                # Add resource if it doesn't exist
                if not exists:
                    # Check if this resource already has a description in another block
                    existing_description = ""
                    for other_block in blocks:
                        if other_block.get("type") == "ai" and "resources" in other_block:
                            for res in other_block["resources"]:
                                if res.get("path") == resource_data.get("path") and res.get("description"):
                                    existing_description = res.get("description", "")
                                    break
                            if existing_description:
                                break

                    # Add the resource with existing description if found
                    resource_to_add = resource_data.copy()
                    if existing_description:
                        resource_to_add["description"] = existing_description

                    block["resources"].append(resource_to_add)
            break

    # Regenerate outline
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return blocks, outline, json_str


def remove_block_resource(blocks, block_id, resource_path, title, description, resources):
    """Remove a resource from a block."""
    # Find the block and remove the resource
    for block in blocks:
        if block["id"] == block_id:
            if "resources" in block:
                # Remove the resource with matching path
                block["resources"] = [res for res in block["resources"] if res.get("path") != resource_path]

                # If this is a text block and we just removed its resource, clear the content
                if block["type"] == "text" and len(block["resources"]) == 0:
                    block["content"] = ""
            break

    # Regenerate outline
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return blocks, outline, json_str


def update_resource_description(blocks, block_id, resource_path, description_text, title, doc_description, resources):
    """Update the description of a resource globally - affects all blocks using this resource."""
    # Update the description in ALL blocks that have this resource
    for block in blocks:
        if "resources" in block:
            for res in block["resources"]:
                if res.get("path") == resource_path:
                    res["description"] = description_text

    # Regenerate outline
    outline, json_str = regenerate_outline_from_state(title, doc_description, resources, blocks)
    return blocks, outline, json_str


def generate_resource_html(resources):
    """Generate HTML for resource panel display."""
    if not resources:
        return (
            "<p style='color: #666; font-size: 12px'>(.docx, .md, .csv, .py, .json, .txt, etc.)</p>"
            "<p style='color: #666; font-size: 12px'>These reference files will be used for AI context.</p>"
        )

    html_items = []
    for idx, resource in enumerate(resources):
        css_class = "resource-item text"
        path = resource["path"].replace("'", "\\'")  # Escape single quotes
        title = resource.get("title", resource["name"])
        description = resource.get("description", "")
        resource_id = f"resource-{idx}"  # Unique ID for each resource

        html_items.append(
            f'<div class="{css_class}" id="{resource_id}" draggable="true" data-resource-name="{resource["name"]}" '
            f'data-resource-title="{title}" data-resource-type="text" data-resource-path="{resource["path"]}">'
            f'<div class="resource-content">'
            f'<div class="resource-header">'
            f'<input type="text" class="resource-title-input" value="{title}" '
            f'placeholder="Title" '
            f"oninput=\"updateResourceTitle('{path}', this.value)\" "
            f'onclick="event.stopPropagation()" />'
            f'<span class="resource-delete" onclick="deleteResourceFromPanel(\'{path}\')">🗑</span>'
            f"</div>"
            f'<div class="resource-description-container">'
            f'<textarea class="resource-panel-description" '
            f'placeholder="Add a description for this resource..." '
            f"oninput=\"updateResourcePanelDescription('{path}', this.value)\" "
            f'onclick="event.stopPropagation()">{description}</textarea>'
            f'<button class="desc-expand-btn" onclick="toggleResourceDescription(\'{resource_id}\')">⌵</button>'
            f"</div>"
            f'<div class="resource-filename">{resource["name"]}</div>'
            f'<div class="resource-upload-zone" data-resource-path="{path}">'
            f'<span class="upload-text">Drop file here to replace</span>'
            f'<input type="file" class="resource-file-input" accept=".txt,.md,.py,.c,.cpp,.h,.java,.js,.ts,.jsx,.tsx,.json,.xml,.yaml,.yml,.toml,.ini,.cfg,.conf,.sh,.bash,.zsh,.fish,.ps1,.bat,.cmd,.rs,.go,.rb,.php,.pl,.lua,.r,.m,.swift,.kt,.scala,.clj,.ex,.exs,.elm,.fs,.ml,.sql,.html,.htm,.css,.scss,.sass,.less,.vue,.svelte,.astro,.tex,.rst,.adoc,.org,.csv,.docx" '
            f"onchange=\"handleResourceFileUpload('{path}', this)\" />"
            f"</div>"
            f"</div>"
            f"</div>"
        )

    return "\n".join(html_items)


def delete_resource_from_panel(resources, resource_path, title, description, blocks):
    """Delete a resource from the resource panel and all blocks that use it."""
    print(f"Deleting resource from panel: {resource_path}")

    # Remove from resources list
    new_resources = [res for res in resources if res.get("path") != resource_path]

    # Create new blocks list to ensure state updates
    updated_blocks = []
    for block in blocks:
        block_copy = block.copy()
        if "resources" in block_copy:
            # Count resources before removal
            original_count = len(block_copy["resources"])

            # Remove the resource
            block_copy["resources"] = [res for res in block_copy["resources"] if res.get("path") != resource_path]

            if original_count != len(block_copy["resources"]):
                print(
                    f"Removed resource from block {block_copy['id']}: {original_count} -> {len(block_copy['resources'])}"
                )

            # If this was a text block and we removed its only resource, clear the content
            if block_copy["type"] == "text" and original_count > 0 and len(block_copy["resources"]) == 0:
                block_copy["content"] = ""

        updated_blocks.append(block_copy)

    # Regenerate outline
    outline, json_str = regenerate_outline_from_state(title, description, new_resources, updated_blocks)

    # Return the values expected by the handler (4 outputs)
    return new_resources, updated_blocks, outline, json_str


def update_resource_title(resources, resource_path, new_title, doc_title, doc_description, blocks):
    """Update the title of a resource."""
    # Update the title in the resources list
    for resource in resources:
        if resource.get("path") == resource_path:
            resource["title"] = new_title
            break

    # Regenerate outline with updated resources (for JSON display)
    outline, json_str = regenerate_outline_from_state(doc_title, doc_description, resources, blocks)

    return resources, outline, json_str


def update_resource_panel_description(resources, resource_path, new_description, doc_title, doc_description, blocks):
    """Update the description of a resource from the panel."""
    # Update the description in the resources list
    for resource in resources:
        if resource.get("path") == resource_path:
            resource["description"] = new_description
            break

    # Regenerate outline with updated resources (for JSON display)
    outline, json_str = regenerate_outline_from_state(doc_title, doc_description, resources, blocks)

    return resources, outline, json_str


def replace_resource_file(
    resources, old_resource_path, new_file_path, doc_title, doc_description, blocks, session_id=None
):
    """Replace a resource file with a new one while keeping the same resource key."""
    import shutil

    # Get or create session ID
    if not session_id:
        session_id = str(uuid.uuid4())

    # Get session files directory
    files_dir = session_manager.get_files_dir(session_id)

    # Copy new file to session directory
    new_file_name = os.path.basename(new_file_path)
    session_file_path = files_dir / new_file_name
    shutil.copy2(new_file_path, session_file_path)

    # Update the resource and all blocks that use it
    for resource in resources:
        if resource.get("path") == old_resource_path:
            # Keep the same key and description, just update the path and name
            resource["path"] = str(session_file_path)
            resource["name"] = new_file_name
            # Keep the existing title - don't update it
            break

    # Update all blocks that reference this resource
    for block in blocks:
        if "resources" in block:
            for block_resource in block["resources"]:
                if block_resource.get("path") == old_resource_path:
                    block_resource["path"] = str(session_file_path)
                    block_resource["name"] = new_file_name
                    # Keep the existing title - don't update it

    # Generate HTML for resources display
    resources_html = generate_resource_html(resources)

    # Regenerate outline with updated resources
    outline, json_str = regenerate_outline_from_state(doc_title, doc_description, resources, blocks)

    # Return updated values including a success flag
    return resources, blocks, gr.update(value=resources_html), outline, json_str, "Resource replaced successfully!"


def load_example(example_id, session_id=None):
    """Load a predefined example based on the example ID."""
    if not example_id:
        return (
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            session_id,
            gr.update(),
            gr.update(),
            gr.update(),
        )

    # Map example IDs to file paths - now using .docpack files
    examples_dir = Path(__file__).parent.parent / "examples"
    example_files = {
        "1": examples_dir / "readme-generation" / "readme.docpack",
        "2": examples_dir / "launch-documentation" / "launch-documentation.docpack",
        "3": examples_dir
        / "scenario-4-annual-performance-review"
        / "Annual Employee Performance Review_20250709_153352.docpack",
    }

    file_path = example_files.get(example_id)
    if not file_path or not file_path.exists():
        # If docpack doesn't exist, show error message
        error_msg = f"Example file not found: {file_path.name if file_path else 'Unknown'}"
        return (
            gr.update(),  # title
            gr.update(),  # description
            gr.update(),  # resources
            gr.update(),  # blocks
            gr.update(),  # outline
            json.dumps({"error": error_msg}, indent=2),  # json_output
            session_id,  # session_id
        )

    # Use the import_outline function to load the example
    result = import_outline(str(file_path), session_id)
    # import_outline now returns 11 values matching import_file.change outputs
    # import_outline returns: title, desc, resources, blocks, outline, json, import_file, session_id, gen_html, gen_content, save_btn
    # load_example needs: title, desc, resources, blocks, outline, json, session_id, gen_html, gen_content, save_btn
    # We need to skip import_file (at index 6) from the result
    return (
        result[0],  # title
        result[1],  # description
        result[2],  # resources
        result[3],  # blocks
        result[4],  # outline
        result[5],  # json_str
        result[7],  # session_id (skip import_file at 6)
        result[8],  # generated_content_html
        result[9],  # generated_content
        result[10],  # save_doc_btn
    )


def import_outline(file_path, session_id=None):
    """Import an outline from a .docpack file and convert to blocks format."""
    if not file_path:
        # Return 11 values matching import_file.change outputs
        return (
            gr.update(),  # title
            gr.update(),  # description
            gr.update(),  # resources
            gr.update(),  # blocks
            gr.update(),  # outline
            gr.update(),  # json_output
            None,  # import_file
            session_id,  # session_state
            gr.update(),  # generated_content_html
            gr.update(),  # generated_content
            gr.update(),  # save_doc_btn
        )

    # Get or create session ID
    if not session_id:
        session_id = str(uuid.uuid4())

    # Define allowed text file extensions
    ALLOWED_EXTENSIONS = {
        ".txt",
        ".md",
        ".py",
        ".c",
        ".cpp",
        ".h",
        ".java",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".json",
        ".xml",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".cfg",
        ".conf",
        ".sh",
        ".bash",
        ".zsh",
        ".fish",
        ".ps1",
        ".bat",
        ".cmd",
        ".rs",
        ".go",
        ".rb",
        ".php",
        ".pl",
        ".lua",
        ".r",
        ".m",
        ".swift",
        ".kt",
        ".scala",
        ".clj",
        ".ex",
        ".exs",
        ".elm",
        ".fs",
        ".ml",
        ".sql",
        ".html",
        ".htm",
        ".css",
        ".scss",
        ".sass",
        ".less",
        ".vue",
        ".svelte",
        ".astro",
        ".tex",
        ".rst",
        ".adoc",
        ".org",
        ".csv",
    }

    try:
        file_path = Path(file_path)

        # Only accept .docpack files
        if file_path.suffix.lower() != ".docpack":
            error_msg = "Import failed: Only .docpack files are supported. Please use a .docpack file created by the Save function."
            return (
                gr.update(),  # title
                gr.update(),  # description
                gr.update(),  # resources
                gr.update(),  # blocks
                gr.update(),  # outline
                json.dumps({"error": error_msg}, indent=2),  # json_output
                None,  # import_file
                session_id,  # session_id
                gr.update(),  # generated_content_html
                gr.update(),  # generated_content
                gr.update(),  # save_doc_btn
            )

        # Use session directory for extraction
        session_dir = session_manager.get_session_dir(session_id)

        # Extract the docpack to session directory
        json_data, extracted_files = DocpackHandler.extract_package(file_path, session_dir)

        # Extract title and description
        title = json_data.get("title", "")
        description = json_data.get("general_instruction", "")

        # Extract and validate resources
        resources = []
        invalid_resources = []
        inline_resources = {}  # Store inline resources by key

        for res_data in json_data.get("resources", []):
            resource_path = res_data.get("path", "")
            resource_name = Path(resource_path).name
            file_ext = Path(resource_name).suffix.lower()

            # Check if this is an inline resource
            if res_data.get("is_inline", False) or res_data.get("key", "").startswith("inline_resource_"):
                # Store inline resource content for later use
                inline_resources[res_data["key"]] = resource_path
                continue  # Don't add to regular resources

            # Check if file extension is allowed
            if file_ext not in ALLOWED_EXTENSIONS:
                invalid_resources.append(f"{resource_name} ({file_ext})")
                continue

            resources.append({
                "key": res_data.get("key", ""),  # Preserve original key
                "path": resource_path,
                "name": resource_name,
                "title": res_data.get("title", resource_name),  # Preserve title or default to filename
                "type": "text",  # All are text files now
                "description": res_data.get("description", ""),
            })

        # If there are invalid resources, show error and return
        if invalid_resources:
            error_msg = "Import failed: The following resources have unsupported file types:\n" + "\n".join(
                invalid_resources
            )
            error_msg += f"\n\nOnly text files are allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            # Return error in the JSON output field
            return (
                gr.update(),  # title
                gr.update(),  # description
                gr.update(),  # resources
                gr.update(),  # blocks
                gr.update(),  # outline
                json.dumps({"error": error_msg}, indent=2),  # json_output
                None,  # import_file
                session_id,  # session_id
                gr.update(),  # generated_content_html
                gr.update(),  # generated_content
                gr.update(),  # save_doc_btn
            )

        # Convert sections to blocks
        blocks = []

        def sections_to_blocks(sections, parent_indent=-1):
            """Recursively convert sections to blocks."""
            for section in sections:
                # Create a block from the section
                block = {
                    "id": str(uuid.uuid4()),
                    "heading": section.get("title", ""),
                    "content": "",
                    "resources": [],
                    "collapsed": True,
                    "indent_level": parent_indent + 1,
                }

                # Determine block type and content
                if "prompt" in section:
                    # AI block
                    block["type"] = "ai"
                    block["content"] = section.get("prompt", "")
                    block["ai_content"] = section.get("prompt", "")

                    # Handle refs
                    refs = section.get("refs", [])
                    if refs and resources:
                        # Map refs back to resources by matching keys
                        for ref in refs:
                            # Find resource with matching key
                            for resource in resources:
                                if resource.get("key") == ref:
                                    block["resources"].append(resource)
                                    break

                elif "resource_key" in section:
                    # Text block
                    block["type"] = "text"
                    block["text_content"] = ""

                    # Handle resource_key
                    resource_key = section.get("resource_key", "")

                    # Check if this is an inline resource
                    if resource_key in inline_resources:
                        # Load content from inline resource file
                        try:
                            inline_path = inline_resources[resource_key]
                            # If it's a relative path in a save directory, construct full path
                            if not Path(inline_path).is_absolute():
                                # Look for the file in the same directory as the imported JSON
                                import_dir = Path(file_path).parent
                                inline_path = import_dir / inline_path

                            with open(inline_path, "r", encoding="utf-8") as f:
                                block["content"] = f.read()
                                block["text_content"] = block["content"]
                                block["edited"] = True  # Mark as edited
                        except Exception as e:
                            print(f"Error loading inline resource: {e}")
                    elif resource_key and resources:
                        # Regular resource reference - find by key
                        for resource in resources:
                            if resource.get("key") == resource_key:
                                block["resources"].append(resource)
                                # Auto-load content from the resource file
                                try:
                                    with open(resource["path"], "r", encoding="utf-8") as f:
                                        block["content"] = f.read()
                                        block["text_content"] = block["content"]
                                except Exception as e:
                                    print(f"Error loading resource content: {e}")
                                break
                else:
                    # Default to AI block if no specific type indicators
                    block["type"] = "ai"

                blocks.append(block)

                # Process nested sections
                if "sections" in section:
                    sections_to_blocks(section["sections"], block["indent_level"])

        # Convert top-level sections
        sections_to_blocks(json_data.get("sections", []))

        # If no blocks were created, add default ones
        if not blocks:
            blocks = [
                {
                    "id": str(uuid.uuid4()),
                    "type": "ai",
                    "heading": "",
                    "content": "",
                    "resources": [],
                    "collapsed": False,
                    "indent_level": 0,
                }
            ]
        else:
            # Ensure the first block is expanded
            if blocks and len(blocks) > 0:
                blocks[0]["collapsed"] = False

        # Regenerate outline and JSON
        outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)

        # Generate resources HTML using the proper function
        generate_resource_html(resources)

        # Return values matching what import_file.change expects
        return (
            title,
            description,
            resources,
            blocks,
            outline,
            json_str,
            None,  # import_file (clear it)
            session_id,
            gr.update(
                value="<em>Click '▷ Generate' to see the generated content here.</em><br><br><br>", visible=True
            ),  # generated_content_html
            gr.update(visible=False),  # generated_content
            gr.update(interactive=False),  # save_doc_btn
        )

    except Exception as e:
        error_msg = f"Error importing file: {str(e)}"
        print(error_msg)
        # Return current values on error matching expected outputs
        return (
            gr.update(),  # title
            gr.update(),  # description
            gr.update(),  # resources
            gr.update(),  # blocks
            gr.update(),  # outline
            gr.update(),  # json_output
            None,  # import_file
            session_id,  # session_state
            gr.update(),  # generated_content_html
            gr.update(),  # generated_content
            gr.update(),  # save_doc_btn
        )


def save_outline(title, outline_json, blocks):
    """Create a .docpack file with all resources bundled and return for download."""
    from datetime import datetime

    try:
        # Create filename from title and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        docpack_name = f"{timestamp}.docpack"

        # Create a temporary file for the docpack
        temp_dir = Path(tempfile.gettempdir())
        docpack_path = temp_dir / docpack_name

        # Parse the current JSON
        current_json = json.loads(outline_json)

        # Collect all resource files and create key mapping
        resource_files = []
        resource_key_map = {}

        for res in current_json.get("resources", []):
            resource_path = Path(res["path"])
            if resource_path.exists():
                resource_files.append(resource_path)
                resource_key_map[str(resource_path.resolve())] = res["key"]

        # Remove is_inline flags before saving
        for res in current_json.get("resources", []):
            if "is_inline" in res:
                del res["is_inline"]

        # Create the docpack with conflict-safe naming
        DocpackHandler.create_package(
            outline_data=current_json,
            resource_files=resource_files,
            output_path=docpack_path,
            resource_key_map=resource_key_map,
        )

        # Return the file path for download
        return gr.update(value=str(docpack_path), visible=True, interactive=True)

    except Exception as e:
        error_msg = f"Error creating docpack: {str(e)}"
        print(error_msg)
        return gr.update(value=None, visible=False)


def create_docpack_from_current_state():
    """Create a docpack using the current global document state."""
    import time
    from datetime import datetime

    global current_document_state

    print(f"=== CREATING DOCPACK at {datetime.now().isoformat()} ===")
    print(f"Title: {current_document_state.get('title', 'N/A') if current_document_state else 'No state'}")
    print(f"Has outline_json: {'outline_json' in current_document_state if current_document_state else False}")
    print(f"Number of blocks: {len(current_document_state.get('blocks', [])) if current_document_state else 0}")
    print(f"Full current_document_state: {current_document_state}")

    if not current_document_state:
        print("ERROR: No current_document_state available for docpack creation")
        return None

    try:
        title = current_document_state.get("title", "Document")
        outline_json = current_document_state.get("outline_json", "{}")
        print(f"DEBUG: Using title '{title}' for docpack filename")

        # Create filename from title and timestamp with milliseconds to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        milliseconds = int(time.time() * 1000) % 1000
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)[:50]
        docpack_name = f"{safe_title}_{timestamp}_{milliseconds}.docpack"
        print(f"DEBUG: Generated filename: {docpack_name} (from title: '{title}', timestamp: {timestamp})")

        # Create a temporary file for the docpack
        temp_dir = Path(tempfile.gettempdir())
        docpack_path = temp_dir / docpack_name

        # Parse the current JSON
        current_json = json.loads(outline_json)

        # Collect all resource files and create key mapping
        resource_files = []
        resource_key_map = {}

        for res in current_json.get("resources", []):
            resource_path = Path(res["path"])
            if resource_path.exists():
                resource_files.append(resource_path)
                resource_key_map[str(resource_path.resolve())] = res["key"]

        # Remove is_inline flags before saving
        for res in current_json.get("resources", []):
            if "is_inline" in res:
                del res["is_inline"]

        # Create the docpack with conflict-safe naming
        DocpackHandler.create_package(
            outline_data=current_json,
            resource_files=resource_files,
            output_path=docpack_path,
            resource_key_map=resource_key_map,
        )

        # Return just the file path
        return str(docpack_path)

    except Exception as e:
        error_msg = f"Error creating docpack: {str(e)}"
        print(error_msg)
        return None


def render_block_resources(block_resources, block_type, block_id):
    """Render the resources inside a block."""
    print(f"render_block_resources for block {block_id}: {len(block_resources) if block_resources else 0} resources")

    if block_type == "text":
        # Text blocks always show the drop zone, never show resources
        return "Drop reference files here to upload text."

    # AI blocks show resources or drop zone
    if not block_resources:
        return "Drop reference files here for AI context."

    html = ""
    for resource in block_resources:
        # Use title if available, otherwise fall back to name
        display_name = resource.get("title", resource.get("name", "Unknown"))
        path = resource.get("path", "").replace("'", "\\'")  # Escape single quotes

        # For AI blocks, show resource without description input and without icon
        html += f"""
        <div class="dropped-resource" data-resource-path="{path}">
            <span class="dropped-resource-title">{display_name}</span>
            <span class="remove-resource" onclick="removeBlockResource('{block_id}', '{path}')">×</span>
        </div>
        """

    return html


def render_blocks(blocks, focused_block_id=None):
    """Render blocks as HTML."""
    import time

    timestamp = int(time.time() * 1000)

    print(f"render_blocks called with {len(blocks) if blocks else 0} blocks at {timestamp}")
    if blocks:
        for i, block in enumerate(blocks):
            res_count = len(block.get("resources", []))
            print(f"  Block {i} ({block['id']}): {res_count} resources")

    if not blocks:
        return "<div class='empty-blocks-message'>Click '+ Add AI' to add an AI generated section.</div><div class='empty-blocks-message'>Click '+ Add Text' to add a traditional text section.</div>"

    html = f"<!-- Rendered at {timestamp} -->\n"
    for i, block in enumerate(blocks):
        block_id = block["id"]
        is_collapsed = block.get("collapsed", False)
        collapsed_class = "collapsed" if is_collapsed else ""
        content_class = "" if is_collapsed else "show"

        if block["type"] == "ai":
            heading_value = block.get("heading", "")
            indent_level = block.get("indent_level", 0)

            # Determine max allowed indent level based on previous block
            max_allowed_indent = 0
            if i > 0:
                prev_block = blocks[i - 1]
                prev_indent = prev_block.get("indent_level", 0)
                max_allowed_indent = prev_indent + 1

            # Build indent controls - always include both buttons, just hide if not applicable
            indent_controls = '<div class="indent-controls">'
            # Show indent button only if we can indent further
            if indent_level < 5 and indent_level < max_allowed_indent:
                indent_controls += (
                    f"<button class=\"indent-btn indent\" onclick=\"updateBlockIndent('{block_id}', 'in')\">⇥</button>"
                )
            else:
                indent_controls += '<div class="indent-btn-placeholder"></div>'

            if indent_level > 0:
                indent_controls += f"<button class=\"indent-btn outdent\" onclick=\"updateBlockIndent('{block_id}', 'out')\">⇤</button>"
            else:
                indent_controls += '<div class="indent-btn-placeholder"></div>'
            indent_controls += "</div>"

            html += f"""
            <div class='content-block ai-block {collapsed_class}' data-id='{block_id}' data-indent='{indent_level}'>
                {indent_controls}
                <button class='collapse-btn' onclick='toggleBlockCollapse("{block_id}")'>
                    <span class='collapse-icon'>⌵</span>
                </button>
                <button class='delete-btn' onclick='deleteBlock("{block_id}")'>🗑</button>
                <button class='add-btn' onclick='addBlockAfter("{block_id}")'>+</button>
                <div class='block-header'>
                    <input type='text' class='block-heading-inline' placeholder='Section Title'
                           value='{heading_value}'
                           onfocus='expandBlockOnHeadingFocus("{block_id}"); setFocusedBlock("{block_id}", true)'
                           oninput='updateBlockHeading("{block_id}", this.value)'/>
                </div>
                <div class='block-content {content_class}'>
                    <div class='block-tabs'>
                        <button class='block-tab active' onclick='focusBlockTextarea("{block_id}")'>AI</button>
                        <button class='block-tab' onclick='convertBlock("{block_id}", "text")'>Text</button>
                    </div>
                    <textarea placeholder='Type your AI instruction here...\nThis text will be used for AI content generation.'
                              onfocus='setFocusedBlock("{block_id}", true)'
                              oninput='updateBlockContent("{block_id}", this.value)'>{block["content"]}</textarea>
                    <div class='block-resources'>
                        {render_block_resources(block.get("resources", []), "AI", block_id)}
                    </div>
                </div>
            </div>
            """
        elif block["type"] == "heading":
            html += f"""
            <div class='content-block heading-block' data-id='{block_id}'>
                <button class='delete-btn' onclick='deleteBlock("{block_id}")'>🗑</button>
                <button class='add-btn' onclick='addBlockAfter("{block_id}")'>+</button>
                <div class='block-header heading-header'>
                    <input type='text' value='{block["content"]}'
                           oninput='updateBlockContent("{block_id}", this.value)'/>
                </div>
            </div>
            """
        elif block["type"] == "text":
            heading_value = block.get("heading", "")
            indent_level = block.get("indent_level", 0)

            # Determine max allowed indent level based on previous block
            max_allowed_indent = 0
            if i > 0:
                prev_block = blocks[i - 1]
                prev_indent = prev_block.get("indent_level", 0)
                max_allowed_indent = prev_indent + 1

            # Build indent controls - always include both buttons, just hide if not applicable
            indent_controls = '<div class="indent-controls">'
            # Show indent button only if we can indent further
            if indent_level < 5 and indent_level < max_allowed_indent:
                indent_controls += (
                    f"<button class=\"indent-btn indent\" onclick=\"updateBlockIndent('{block_id}', 'in')\">⇥</button>"
                )
            else:
                indent_controls += '<div class="indent-btn-placeholder"></div>'

            if indent_level > 0:
                indent_controls += f"<button class=\"indent-btn outdent\" onclick=\"updateBlockIndent('{block_id}', 'out')\">⇤</button>"
            else:
                indent_controls += '<div class="indent-btn-placeholder"></div>'
            indent_controls += "</div>"

            html += f"""
            <div class='content-block text-block {collapsed_class}' data-id='{block_id}' data-indent='{indent_level}'>
                {indent_controls}
                <button class='collapse-btn' onclick='toggleBlockCollapse("{block_id}")'>
                    <span class='collapse-icon'>⌵</span>
                </button>
                <button class='delete-btn' onclick='deleteBlock("{block_id}")'>🗑</button>
                <button class='add-btn' onclick='addBlockAfter("{block_id}")'>+</button>
                <div class='block-header'>
                    <input type='text' class='block-heading-inline' placeholder='Section Title'
                           value='{heading_value}'
                           onfocus='expandBlockOnHeadingFocus("{block_id}"); setFocusedBlock("{block_id}", true)'
                           oninput='updateBlockHeading("{block_id}", this.value)'/>
                </div>
                <div class='block-content {content_class}'>
                    <div class='block-tabs'>
                        <button class='block-tab' onclick='convertBlock("{block_id}", "ai")'>AI</button>
                        <button class='block-tab active' onclick='focusBlockTextarea("{block_id}")'>Text</button>
                    </div>
                    <textarea placeholder='Type your text here...\nThis text will be copied into your document.'
                              onfocus='setFocusedBlock("{block_id}", true)'
                              oninput='updateBlockContent("{block_id}", this.value)'>{block["content"]}</textarea>
                    <div class='block-resources'>
                        {render_block_resources(block.get("resources", []), "text", block_id)}
                    </div>
                </div>
            </div>
            """

    return html


def handle_start_file_upload(files, current_resources):
    """Handle file uploads on the Start tab."""
    if not files:
        return current_resources, None, gr.update(visible=False)

    # Add new files to resources
    new_resources = current_resources.copy() if current_resources else []
    warnings = []

    for file_path in files:
        if file_path:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            # Check if it's a docx file and if it's protected
            if file_path.lower().endswith('.docx'):
                is_protected, error_msg = check_docx_protected(file_path)
                if is_protected:
                    warnings.append(error_msg)
                    continue  # Skip adding this file to resources

            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"

            # Check if already in resources (by name)
            if not any(r["name"] == file_name for r in new_resources):
                new_resources.append({
                    "path": file_path,
                    "name": file_name,
                    "size": size_str,
                })

    # Create warning message if there were any protected files
    if warnings:
        import random
        warning_id = f"warning_{random.randint(1000, 9999)}"
        warning_html = f"""
        <div id="{warning_id}" style='position: relative; color: #dc2626; background: #fee2e2; padding: 8px 30px 8px 12px; border-radius: 4px; margin-top: 8px; font-size: 14px;'>
            <button onclick="document.getElementById('{warning_id}').style.display='none'" 
                    style='position: absolute; top: 4px; right: 5px; background: none; border: none; color: #dc2626; font-size: 18px; cursor: pointer; padding: 0 5px; opacity: 0.6;' 
                    onmouseover="this.style.opacity='1'" 
                    onmouseout="this.style.opacity='0.6'"
                    title='Close'>×</button>
            {"<br>".join(warnings)}
        </div>
        """
        return new_resources, None, gr.update(value=warning_html, visible=True)
    
    return new_resources, None, gr.update(visible=False)


def handle_start_draft_click_wrapper(prompt, resources, session_id=None):
    """Wrapper to handle the Draft button click synchronously."""
    print("DEBUG: handle_start_draft_click_wrapper called")
    print(f"DEBUG: prompt type: {type(prompt)}, value: '{prompt}'")
    print(f"DEBUG: resources type: {type(resources)}, value: {resources}")
    print(f"DEBUG: session_id: {session_id}")

    # Run the async function synchronously

    return asyncio.run(handle_start_draft_click(prompt, resources, session_id))


async def handle_start_draft_click(prompt, resources, session_id=None):
    """Handle the Draft button click on the Start tab."""
    print("DEBUG: In async handle_start_draft_click")
    print(f"DEBUG: prompt value in async: '{prompt}'")

    if not prompt or not prompt.strip():
        error_msg = "Please enter a description of what you'd like to create."
        print(f"DEBUG: No prompt provided, returning error: {error_msg}")
        # Return 15 values to match outputs (added loading message and button)
        return (
            gr.update(),  # doc_title
            gr.update(),  # doc_description
            gr.update(),  # resources_state
            gr.update(),  # blocks_state
            gr.update(),  # outline_state
            gr.update(),  # json_output
            session_id,  # session_state
            gr.update(),  # generated_content_html
            gr.update(),  # generated_content
            gr.update(),  # save_doc_btn
            gr.update(),  # switch_tab_trigger
            gr.update(
                value=f'''<div id="prompt_error" style="position: relative; color: #dc2626; padding: 8px 30px 8px 12px; background: #fee2e2; border-radius: 4px; margin-top: 8px; font-size: 14px;">
                    <button onclick="document.getElementById('prompt_error').style.display='none'" 
                            style="position: absolute; top: 4px; right: 5px; background: none; border: none; color: #dc2626; font-size: 18px; cursor: pointer; padding: 0 5px; opacity: 0.6;" 
                            onmouseover="this.style.opacity='1'" 
                            onmouseout="this.style.opacity='0.6'"
                            title="Close">×</button>
                    {error_msg}
                </div>''',
                visible=True,
            ),  # start_error_message
            gr.update(),  # start_prompt_input - no change
            gr.update(interactive=True),  # get_started_btn
        )

    try:
        # Get or create session ID
        if not session_id:
            session_id = str(uuid.uuid4())
            print(f"DEBUG: Created new session_id: {session_id}")

        print(f"DEBUG: Calling generate_docpack_from_prompt with {len(resources) if resources else 0} resources")

        # Call the docpack generation function
        docpack_path, outline_json = await generate_docpack_from_prompt(
            prompt=prompt.strip(), resources=resources or [], session_id=session_id, dev_mode=IS_DEV_MODE
        )

        print(f"DEBUG: Received docpack_path: {docpack_path}")
        print(f"DEBUG: Received outline_json length: {len(outline_json) if outline_json else 0}")

        # Parse the outline JSON
        if outline_json:
            outline_data = json.loads(outline_json)
            print(f"DEBUG: Successfully parsed outline with title: {outline_data.get('title', 'No title')}")

            # Process the outline data similar to import_outline function
            title = outline_data.get("title", "Untitled Document")
            description = outline_data.get("general_instruction", "")

            # Process resources
            resources = []
            session_files_dir = session_manager.get_files_dir(session_id)

            for res_data in outline_data.get("resources", []):
                resource_path = res_data.get("path", "")
                if resource_path:
                    # Copy resource to session files directory if it exists
                    source_path = Path(resource_path)
                    if source_path.exists():
                        target_path = session_files_dir / source_path.name
                        if source_path != target_path:
                            import shutil

                            shutil.copy2(source_path, target_path)

                        resources.append({
                            "key": res_data.get("key", ""),
                            "name": source_path.name,
                            "path": str(target_path),
                            "description": res_data.get("description", ""),
                        })

            # Convert sections to blocks
            blocks = []

            def sections_to_blocks(sections, parent_indent=-1):
                """Recursively convert sections to blocks."""
                for section in sections:
                    block = {
                        "id": str(uuid.uuid4()),
                        "heading": section.get("title", ""),
                        "content": "",
                        "resources": [],
                        "collapsed": True,
                        "indent_level": parent_indent + 1,
                    }

                    if "prompt" in section:
                        # AI block
                        block["type"] = "ai"
                        block["content"] = section.get("prompt", "")
                        block["ai_content"] = section.get("prompt", "")

                        # Handle refs
                        refs = section.get("refs", [])
                        if refs and resources:
                            for ref in refs:
                                for resource in resources:
                                    if resource.get("key") == ref:
                                        block["resources"].append(resource)
                                        break
                    else:
                        # Text block
                        block["type"] = "text"
                        block["content"] = ""

                    blocks.append(block)

                    # Process nested sections
                    if "sections" in section and section["sections"]:
                        sections_to_blocks(section["sections"], parent_indent=block["indent_level"])

            # Convert top-level sections
            sections_to_blocks(outline_data.get("sections", []))

            # Ensure the first block is expanded (consistent with import behavior)
            if blocks and len(blocks) > 0:
                blocks[0]["collapsed"] = False

            # Generate the JSON for the outline
            outline = json_to_outline(outline_data)
            json_str = json.dumps(outline_data, indent=2)

            # Return all the values needed to populate the Draft+Generate tab
            # This matches what import_outline returns
            # DO NOT switch to the draft tab yet - that will happen in the next step
            return (
                title,  # doc_title
                description,  # doc_description
                resources,  # resources_state
                blocks,  # blocks_state
                outline,  # outline_state
                json_str,  # json_output
                session_id,  # session_state
                gr.update(visible=False),  # generated_content_html
                gr.update(visible=False),  # generated_content
                gr.update(interactive=False),  # save_doc_btn
                gr.update(visible=True, value=f"SWITCH_TO_DRAFT_TAB_{int(time.time() * 1000)}"),  # switch_tab_trigger
                gr.update(visible=False),  # start_error_message - hide on success
                gr.update(
                    lines=4, max_lines=10, interactive=True, elem_classes="start-prompt-input"
                ),  # start_prompt_input - preserve value but reset display properties
                gr.update(interactive=True),  # get_started_btn
            )
        else:
            error_msg = "Failed to generate outline. Please try again."
            print(f"DEBUG: No outline generated, returning error: {error_msg}")
            # Return 15 values to match outputs
            return (
                gr.update(),  # doc_title
                gr.update(),  # doc_description
                gr.update(),  # resources_state
                gr.update(),  # blocks_state
                gr.update(),  # outline_state
                gr.update(),  # json_output
                session_id,  # session_state
                gr.update(),  # generated_content_html
                gr.update(),  # generated_content
                gr.update(),  # save_doc_btn
                gr.update(),  # switch_tab_trigger
                gr.update(
                    value=f'''<div id="outline_error" style="position: relative; color: #dc2626; padding: 8px 30px 8px 12px; background: #fee2e2; border-radius: 4px; margin-top: 8px; font-size: 14px;">
                        <button onclick="document.getElementById('outline_error').style.display='none'" 
                                style="position: absolute; top: 4px; right: 5px; background: none; border: none; color: #dc2626; font-size: 18px; cursor: pointer; padding: 0 5px; opacity: 0.6;" 
                                onmouseover="this.style.opacity='1'" 
                                onmouseout="this.style.opacity='0.6'"
                                title="Close">×</button>
                        {error_msg}
                    </div>''',
                    visible=True,
                ),  # start_error_message
                gr.update(lines=4, max_lines=10),  # start_prompt_input - preserve lines
                gr.update(interactive=True),  # get_started_btn
            )

    except Exception as e:
        import traceback

        error_msg = f"Error: {str(e)}"
        print(f"ERROR in handle_start_draft_click: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        # Return 15 values to match outputs
        return (
            gr.update(),  # doc_title
            gr.update(),  # doc_description
            gr.update(),  # resources_state
            gr.update(),  # blocks_state
            gr.update(),  # outline_state
            gr.update(),  # json_output
            session_id,  # session_state
            gr.update(),  # generated_content_html
            gr.update(),  # generated_content
            gr.update(),  # save_doc_btn
            gr.update(),  # switch_tab_trigger
            gr.update(
                value=f'''<div id="exception_error" style="position: relative; color: #dc2626; padding: 8px 30px 8px 12px; background: #fee2e2; border-radius: 4px; margin-top: 8px; font-size: 14px;">
                    <button onclick="document.getElementById('exception_error').style.display='none'" 
                            style="position: absolute; top: 4px; right: 5px; background: none; border: none; color: #dc2626; font-size: 18px; cursor: pointer; padding: 0 5px; opacity: 0.6;" 
                            onmouseover="this.style.opacity='1'" 
                            onmouseout="this.style.opacity='0.6'"
                            title="Close">×</button>
                    {error_msg}
                </div>''',
                visible=True,
            ),  # start_error_message
            gr.update(),  # start_prompt_input
            gr.update(interactive=True),  # get_started_btn
        )


def handle_file_upload(files, current_resources, title, description, blocks, session_id=None):
    """Handle uploaded files and return HTML display of file names."""
    if not files:
        # Don't return None for outline and json_output to avoid clearing them
        # Don't hide warning on empty upload - keep existing warning visible
        return current_resources, None, gr.update(), gr.update(), session_id, gr.update()

    # Debug: Check what we're receiving
    print(f"DEBUG handle_file_upload - title: {title}, description: {description}, blocks: {blocks}")

    # Get or create session ID
    if not session_id:
        session_id = str(uuid.uuid4())

    # Add new files to resources
    new_resources = current_resources.copy() if current_resources else []
    warnings = []

    # Get session files directory
    files_dir = session_manager.get_files_dir(session_id)

    for file_path in files:
        if file_path:
            import shutil

            file_name = os.path.basename(file_path)
            
            # Check if it's a docx file and if it's protected
            if file_path.lower().endswith('.docx'):
                is_protected, error_msg = check_docx_protected(file_path)
                if is_protected:
                    warnings.append(error_msg)
                    continue  # Skip adding this file to resources

            # Copy file to session directory
            session_file_path = files_dir / file_name
            shutil.copy2(file_path, session_file_path)

            # Check if already in resources (by name)
            if not any(r["name"] == file_name for r in new_resources):
                # All uploaded files are text files now
                new_resources.append({
                    "path": str(session_file_path),
                    "name": file_name,
                    "title": file_name,  # Default title is the filename
                    "type": "text",
                    "description": "",  # Initialize with empty description
                })

    # Regenerate outline with new resources
    outline, json_str = regenerate_outline_from_state(title, description, new_resources, blocks)

    # Debug: Check what we're returning
    print(f"DEBUG handle_file_upload - returning json_str: {json_str[:100]}...")
    print("DEBUG handle_file_upload - full return values:")
    print(f"  - new_resources length: {len(new_resources)}")
    print("  - file_upload clear: None")
    print(f"  - outline type: {type(outline)}")
    print(f"  - json_str type: {type(json_str)}, length: {len(json_str)}")
    print(f"  - session_id: {session_id}")

    # Create warning message if there were any protected files
    if warnings:
        import random
        warning_id = f"warning_{random.randint(1000, 9999)}"
        warning_html = f"""
        <div id="{warning_id}" style='position: relative; color: #dc2626; background: #fee2e2; padding: 10px 30px 10px 12px; border-radius: 4px; margin: 10px 0;'>
            <button onclick="document.getElementById('{warning_id}').style.display='none'" 
                    style='position: absolute; top: 5px; right: 5px; background: none; border: none; color: #dc2626; font-size: 18px; cursor: pointer; padding: 0 5px; opacity: 0.6;' 
                    onmouseover="this.style.opacity='1'" 
                    onmouseout="this.style.opacity='0.6'"
                    title='Close'>×</button>
            {"<br>".join(warnings)}
            <br><small style='color: #991b1b; margin-top: 5px; display: block;'>Protected files were not added to resources.</small>
        </div>
        """
        warning_update = gr.update(value=warning_html, visible=True)
    else:
        warning_update = gr.update(visible=False)
    
    return (
        new_resources,
        None,  # Clear file upload
        outline,
        json_str,
        session_id,
        warning_update,
    )


# Global variable to store current document state for download
current_document_state = {"title": "", "outline_json": "{}", "blocks": []}


def update_resource_title_gradio(resources, resource_path, new_title, title, description, blocks):
    """Update resource title from Gradio component."""
    for resource in resources:
        if resource["path"] == resource_path:
            resource["title"] = new_title
            break

    # Update title in all blocks that have this resource
    for block in blocks:
        if "resources" in block:
            for res in block["resources"]:
                if res.get("path") == resource_path:
                    res["title"] = new_title

    # Regenerate outline
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return resources, outline, json_str


def update_resource_description_gradio(resources, resource_path, new_description, title, description, blocks):
    """Update resource description from Gradio component."""
    for resource in resources:
        if resource["path"] == resource_path:
            resource["description"] = new_description
            break

    # Update description in ALL blocks that have this resource
    for block in blocks:
        if "resources" in block:
            for res in block["resources"]:
                if res.get("path") == resource_path:
                    res["description"] = new_description

    # Regenerate outline
    outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
    return resources, outline, json_str


def delete_resource_gradio(resources, resource_path, title, description, blocks):
    """Delete a resource from Gradio component."""
    print(f"Deleting resource: {resource_path}")

    # Remove from resources list
    new_resources = [res for res in resources if res.get("path") != resource_path]

    # Also remove from all blocks that have this resource
    updated_blocks = []
    for block in blocks:
        block_copy = block.copy()
        if "resources" in block_copy:
            # Remove the resource with matching path
            original_count = len(block_copy["resources"])
            block_copy["resources"] = [res for res in block_copy["resources"] if res.get("path") != resource_path]
            new_count = len(block_copy["resources"])

            if original_count != new_count:
                print(f"Removed resource from block {block_copy['id']}: {original_count} -> {new_count}")

            # If this is a text block and we just removed its resource, clear the content
            if block_copy["type"] == "text" and len(block_copy["resources"]) == 0:
                block_copy["content"] = ""

        updated_blocks.append(block_copy)

    # Regenerate outline
    outline, json_str = regenerate_outline_from_state(title, description, new_resources, updated_blocks)
    # Return blocks too so the UI updates
    return new_resources, updated_blocks, outline, json_str


def replace_resource_file_gradio(resources, old_resource_path, new_file, title, description, blocks, session_id=None):
    """Replace a resource file from Gradio component."""
    if not new_file:
        return resources, None, "{}", None, gr.update(visible=False)

    try:
        # Check if the new file is a protected docx
        if new_file.name.lower().endswith('.docx'):
            is_protected, error_msg = check_docx_protected(new_file.name)
            if is_protected:
                import random
                warning_id = f"warning_{random.randint(1000, 9999)}"
                warning_html = f"""
                <div id="{warning_id}" style='position: relative; color: #dc2626; background: #fee2e2; padding: 8px 25px 8px 8px; border-radius: 4px; margin: 5px 0; font-size: 13px;'>
                    <button onclick="document.getElementById('{warning_id}').style.display='none'" 
                            style='position: absolute; top: 2px; right: 2px; background: none; border: none; color: #dc2626; font-size: 16px; cursor: pointer; padding: 0 3px; line-height: 1; opacity: 0.6;' 
                            onmouseover="this.style.opacity='1'" 
                            onmouseout="this.style.opacity='0.6'"
                            title='Close'>×</button>
                    <strong>⚠️ Cannot Replace:</strong><br>{error_msg}
                </div>
                """
                return resources, None, "{}", None, gr.update(value=warning_html, visible=True)
        
        # Get or create session
        if not session_id:
            session_id = str(uuid.uuid4())

        session_dir = session_manager.get_session_dir(session_id)

        # Copy new file to session directory
        new_file_path = Path(new_file.name)
        new_filename = new_file_path.name
        dest_path = session_dir / new_filename

        # If the new file has the same name as an existing file, add a suffix
        counter = 1
        while dest_path.exists() and str(dest_path) != old_resource_path:
            stem = new_file_path.stem
            suffix = new_file_path.suffix
            new_filename = f"{stem}_{counter}{suffix}"
            dest_path = session_dir / new_filename
            counter += 1

        # Copy the file
        import shutil

        shutil.copy2(new_file.name, dest_path)

        # Update resources list
        for i, resource in enumerate(resources):
            if resource["path"] == old_resource_path:
                # Keep the same title and description
                old_title = resource.get("title", "")
                old_description = resource.get("description", "")

                # Update the resource
                resources[i] = {
                    "name": new_filename,
                    "path": str(dest_path),
                    "title": old_title if old_title else new_filename,
                    "description": old_description,
                }

                # Update in all blocks
                for block in blocks:
                    if "resources" in block:
                        for j, res in enumerate(block["resources"]):
                            if res.get("path") == old_resource_path:
                                block["resources"][j] = {
                                    "path": str(dest_path),
                                    "title": old_title if old_title else new_filename,
                                    "description": old_description,
                                }

                                # If it's a text block, reload the content
                                if block["type"] == "text":
                                    try:
                                        if dest_path.lower().endswith('.docx'):
                                            # Extract text from docx file
                                            block["content"] = docx_to_text(dest_path)
                                        else:
                                            # Read as regular text file
                                            with open(dest_path, "r", encoding="utf-8") as f:
                                                block["content"] = f.read()
                                    except Exception as e:
                                        print(f"Error loading new file content: {e}")

                break

        # Regenerate outline
        outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)

        # Return with cleared file input and no warning
        return resources, outline, json_str, None, gr.update(visible=False)

    except Exception as e:
        print(f"Error replacing resource file: {e}")
        import random
        warning_id = f"warning_{random.randint(1000, 9999)}"
        # Check if it's a protection error
        if "protected or encrypted" in str(e):
            warning_html = f"""
            <div id="{warning_id}" style='position: relative; color: #dc2626; background: #fee2e2; padding: 8px 25px 8px 8px; border-radius: 4px; margin: 5px 0; font-size: 13px;'>
                <button onclick="document.getElementById('{warning_id}').style.display='none'" 
                        style='position: absolute; top: 2px; right: 2px; background: none; border: none; color: #dc2626; font-size: 16px; cursor: pointer; padding: 0 3px; line-height: 1; opacity: 0.6;' 
                        onmouseover="this.style.opacity='1'" 
                        onmouseout="this.style.opacity='0.6'"
                        title='Close'>×</button>
                <strong>⚠️ Replace Failed:</strong><br>{str(e)}
            </div>
            """
            return resources, None, "{}", None, gr.update(value=warning_html, visible=True)
        # For other errors, show a generic error message
        warning_html = f"""
        <div id="{warning_id}" style='position: relative; color: #92400e; background: #fef3c7; padding: 8px 25px 8px 8px; border-radius: 4px; margin: 5px 0; font-size: 13px;'>
            <button onclick="document.getElementById('{warning_id}').style.display='none'" 
                    style='position: absolute; top: 2px; right: 2px; background: none; border: none; color: #92400e; font-size: 16px; cursor: pointer; padding: 0 3px; line-height: 1; opacity: 0.6;' 
                    onmouseover="this.style.opacity='1'" 
                    onmouseout="this.style.opacity='0.6'"
                    title='Close'>×</button>
            <strong>⚠️ Error:</strong><br>Failed to replace file: {str(e)}
        </div>
        """
        return resources, None, "{}", None, gr.update(value=warning_html, visible=True)


def create_app():
    """Create and return the Document Builder Gradio app."""

    # Load custom CSS
    css_path = Path(__file__).parent / "static" / "css" / "styles.css"
    with open(css_path, "r") as f:
        custom_css = f.read()

    # Load custom JavaScript
    js_path = Path(__file__).parent / "static" / "js" / "script.js"
    with open(js_path, "r") as f:
        js_content = f.read()

    # Wrap JS in script tags for head injection
    custom_js = f"<script>{js_content}</script>"

    with gr.Blocks(title="Document Generator", css=custom_css, head=custom_js) as app:
        # Needed to declare up front, so elements will appear in deployed DOM
        gr.DownloadButton(visible=True, elem_classes="hidden-component")
        gr.File(visible=True, elem_classes="hidden-component")
        gr.Textbox(visible=True, elem_classes="hidden-component")
        gr.TextArea(visible=True, elem_classes="hidden-component")
        gr.Code(visible=True, elem_classes="hidden-component")

        # Shared session state for the entire app
        session_state = gr.State(None)

        # Main app layout
        with gr.Tab("Draft", id="start_tab"):
            # State for start tab resources
            start_resources_state = gr.State([])

            with gr.Column(elem_classes="start-tab-container"):
                # Big centered welcome message
                gr.Markdown("# Welcome to Document Generator", elem_classes="start-welcome-title")
                gr.Markdown("Draft once. Regenerate forever.", elem_classes="start-welcome-subtitle")

                # Single expanding card
                with gr.Column(elem_classes="start-input-card-container"):
                    with gr.Column(elem_classes="start-input-card"):
                        gr.TextArea(
                            label="What document would you like to create?",
                            elem_classes="resource-drop-label",
                        )
                        # Example buttons container - always visible at the top
                        with gr.Column(elem_classes="start-examples-container"):
                            with gr.Row(elem_classes="start-examples-buttons"):
                                example_code_readme_btn = gr.Button(
                                    "📝 Code README", variant="secondary", size="sm", elem_classes="start-example-btn"
                                )
                                example_product_launch_btn = gr.Button(
                                    "🚀 Product Launch",
                                    variant="secondary",
                                    size="sm",
                                    elem_classes="start-example-btn",
                                )
                                example_performance_review_btn = gr.Button(
                                    "📈 Performance Review",
                                    variant="secondary",
                                    size="sm",
                                    elem_classes="start-example-btn",
                                )

                        # User prompt input
                        start_prompt_input = gr.TextArea(
                            placeholder="Describe your structured document here...\n",
                            show_label=False,
                            elem_classes="start-prompt-input",
                            lines=4,
                            max_lines=10,
                            elem_id="start-prompt-input",
                            value="",  # Explicitly set initial value
                        )

                        # Error message component (hidden by default)
                        start_error_message = gr.HTML(value="", visible=False, elem_classes="start-error-message")

                        # Expandable content within the same card
                        with gr.Column(elem_classes="start-expandable-content", elem_id="start-expandable-section"):
                            # Display uploaded resources (above dropzone and button)
                            with gr.Column(elem_classes="start-resources-display-container"):
                                # Create a placeholder for the resources displayfvz
                                start_resources_display = gr.HTML(
                                    value='<div class="start-resources-list"></div>',
                                    elem_classes="start-resources-display",
                                )

                                # Function to render resources
                                def render_start_resources(resources):
                                    print(
                                        f"DEBUG render_start_resources called with {len(resources) if resources else 0} resources"
                                    )
                                    if resources and len(resources) > 0:
                                        # Create a flex container for resources
                                        html_content = '<div class="start-resources-list">'
                                        for idx, resource in enumerate(resources):
                                            print(f"  Rendering resource: {resource['name']}")
                                            html_content += f"""
                                                <div class="dropped-resource">
                                                    <span>{resource["name"]}</span>
                                                    <button class="remove-resource" onclick="event.stopPropagation(); removeStartResourceByIndex({idx}, '{resource["name"]}'); return false;">🗑</button>
                                                </div>
                                            """
                                        html_content += "</div>"
                                        return html_content
                                    else:
                                        # Return empty div when no resources
                                        return '<div class="start-resources-list"></div>'

                            # Upload area - full width
                            gr.TextArea(
                                label="Add reference files for AI context. (.docx, .md, .csv, .py, .json, .txt, etc.)",
                                elem_classes="resource-drop-label",
                            )
                            # File upload dropzone
                            start_file_upload = gr.File(
                                label="Drop files here or click to upload",
                                file_count="multiple",
                                file_types=SUPPORTED_FILE_TYPES,
                                elem_classes="start-file-upload-dropzone",
                                show_label=False,
                                height=90,
                            )
                            
                            # Warning message for protected files
                            start_upload_warning = gr.HTML(visible=False)

                            # Draft button - full width below dropzone
                            get_started_btn = gr.Button(
                                "Draft",
                                variant="primary",
                                size="sm",
                                elem_classes="start-get-started-btn start-draft-btn",
                                elem_id="start-get-started-btn",
                            )

                # Main feature card with three examples
                with gr.Column(elem_classes="start-feature-card"):
                    gr.Markdown("### Why Choose Document Generator?", elem_classes="start-feature-title")
                    gr.Markdown(
                        "Build living document templates you control. Fine-tune sections, lock in what works, regenerate what needs updating. Perfect for content that evolves with your codebase, grows with new resources, or needs to stay current automatically.",
                        elem_classes="start-feature-description",
                    )

                    # Three feature columns
                    with gr.Row(elem_classes="start-features-grid"):
                        with gr.Column(scale=1, elem_classes="start-feature-item"):
                            template_img_path = (
                                Path(__file__).parent / "static" / "images" / "template_control-removebg-preview.jpg"
                            )
                            gr.Image(
                                value=str(template_img_path),
                                show_label=False,
                                height=150,
                                container=False,
                                elem_classes="start-feature-image",
                                elem_id="template-control-image",
                                show_download_button=False,
                                show_fullscreen_button=False,
                                interactive=False,
                            )
                            gr.Markdown("### Template Control", elem_classes="start-feature-item-title")
                            gr.Markdown(
                                "Get started fast, then own the template. Update sections, adjust prompts, fine-tune your design. Maintain exactly the structure you need.",
                                elem_classes="start-feature-item-text",
                            )

                        with gr.Column(scale=1, elem_classes="start-feature-item"):
                            evergreen_img_path = (
                                Path(__file__).parent / "static" / "images" / "evergreen_content-removebg-preview.jpg"
                            )
                            gr.Image(
                                value=str(evergreen_img_path),
                                show_label=False,
                                height=150,
                                container=False,
                                elem_classes="start-feature-image",
                                elem_id="evergreen-content-image",
                                show_download_button=False,
                                show_fullscreen_button=False,
                                interactive=False,
                            )
                            gr.Markdown("### Evergreen Content", elem_classes="start-feature-item-title")
                            gr.Markdown(
                                "Link to evolving resources - code, docs, notes. Regenerate anytime to pull in the latest context. Perfect for READMEs, API docs, or any content that tracks changing information.",
                                elem_classes="start-feature-item-text",
                            )

                        with gr.Column(scale=1, elem_classes="start-feature-item"):
                            smart_img_path = (
                                Path(__file__).parent / "static" / "images" / "smart_regeneration-removebg-preview.jpg"
                            )
                            gr.Image(
                                value=str(smart_img_path),
                                show_label=False,
                                height=150,
                                container=False,
                                elem_classes="start-feature-image",
                                elem_id="smart-regeneration-image",
                                show_download_button=False,
                                show_fullscreen_button=False,
                                interactive=False,
                            )
                            gr.Markdown("### Smart Regeneration", elem_classes="start-feature-item-title")
                            gr.Markdown(
                                "Refresh while keeping refined content intact. Regenerate specific parts with new data - your polished introduction stays perfect while metrics update automatically.",
                                elem_classes="start-feature-item-text",
                            )

                # Process section
                with gr.Column(elem_classes="start-process-section"):
                    gr.Markdown("## How It Works", elem_classes="start-process-title")
                    gr.Markdown(
                        "Three simple steps to transform your ideas into polished documents",
                        elem_classes="start-process-subtitle",
                    )

                    with gr.Row(elem_classes="start-process-container"):
                        # Left side - Steps
                        with gr.Column(scale=1, elem_classes="start-process-steps-vertical"):
                            # Step 1
                            with gr.Row(elem_classes="start-process-step-vertical start-step-1"):
                                with gr.Column(scale=0, min_width=60, elem_classes="start-step-number-col"):
                                    gr.Markdown("1", elem_classes="start-step-number-vertical")
                                with gr.Column(scale=1, elem_classes="start-step-content"):
                                    gr.Markdown("### Draft Your Template", elem_classes="start-step-title")
                                    gr.Markdown(
                                        "Start with AI assistance to create your initial document structure. Describe what you need and upload reference materials.",
                                        elem_classes="start-step-description",
                                    )

                            # Step 2
                            with gr.Row(elem_classes="start-process-step-vertical start-step-2"):
                                with gr.Column(scale=0, min_width=60, elem_classes="start-step-number-col"):
                                    gr.Markdown("2", elem_classes="start-step-number-vertical")
                                with gr.Column(scale=1, elem_classes="start-step-content"):
                                    gr.Markdown("### Edit & Update", elem_classes="start-step-title")
                                    gr.Markdown(
                                        "Refine your outline and keep resources current. Update reference files as content changes, adjust prompts, and reorganize sections to match your evolving needs.",
                                        elem_classes="start-step-description",
                                    )

                            # Step 3
                            with gr.Row(elem_classes="start-process-step-vertical start-step-3"):
                                with gr.Column(scale=0, min_width=60, elem_classes="start-step-number-col"):
                                    gr.Markdown("3", elem_classes="start-step-number-vertical")
                                with gr.Column(scale=1, elem_classes="start-step-content"):
                                    gr.Markdown("### Generate & Export", elem_classes="start-step-title")
                                    gr.Markdown(
                                        "Click generate to create your final document. Export in multiple formats and regenerate anytime with updated content.",
                                        elem_classes="start-step-description",
                                    )

                        # Right side - Visual placeholder
                        with gr.Column(scale=1, elem_classes="start-process-visual"):
                            gr.HTML(
                                """
                                <div class="process-visual-placeholder">
                                    <div class="visual-content">
                                        <svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
                                            <!-- Document icon -->
                                            <rect x="100" y="50" width="200" height="250" rx="8" fill="#f0f9f9" stroke="#4a9d9e" stroke-width="2"/>

                                            <!-- Lines representing text -->
                                            <rect x="120" y="80" width="160" height="8" rx="4" fill="#4a9d9e" opacity="0.3"/>
                                            <rect x="120" y="100" width="140" height="8" rx="4" fill="#4a9d9e" opacity="0.3"/>
                                            <rect x="120" y="120" width="150" height="8" rx="4" fill="#4a9d9e" opacity="0.3"/>

                                            <!-- AI sparkle -->
                                            <g transform="translate(250, 70)">
                                                <path d="M0,-10 L3,-3 L10,0 L3,3 L0,10 L-3,3 L-10,0 L-3,-3 Z" fill="#4a9d9e" opacity="0.8"/>
                                            </g>

                                            <!-- Sections -->
                                            <rect x="120" y="150" width="160" height="40" rx="4" fill="#e8f5f5" stroke="#4a9d9e" stroke-width="1"/>
                                            <rect x="120" y="200" width="160" height="40" rx="4" fill="#e8f5f5" stroke="#4a9d9e" stroke-width="1"/>
                                            <rect x="120" y="250" width="160" height="40" rx="4" fill="#e8f5f5" stroke="#4a9d9e" stroke-width="1"/>
                                        </svg>
                                        <p class="visual-caption">Your document takes shape with AI assistance</p>
                                    </div>
                                </div>
                            """,
                                elem_classes="start-process-visual-content",
                            )

        # Second tab - Existing Document Builder content
        with gr.Tab("Update + Generate", id="document_builder_tab"):
            # State to track resources and blocks
            resources_state = gr.State([])
            focused_block_state = gr.State(None)

            # Initialize with default blocks
            initial_blocks = [
                {
                    "id": str(uuid.uuid4()),
                    "type": "ai",
                    "heading": "",
                    "content": "",
                    "resources": [],
                    "collapsed": False,  # AI block starts expanded
                    "indent_level": 0,
                },
                {
                    "id": str(uuid.uuid4()),
                    "type": "text",
                    "heading": "",
                    "content": "",
                    "resources": [],
                    "collapsed": True,  # Text block starts collapsed
                    "indent_level": 0,
                },
            ]
            blocks_state = gr.State(initial_blocks)

            # Initialize outline state with empty values
            initial_outline, initial_json = regenerate_outline_from_state("", "", [], initial_blocks)
            outline_state = gr.State(initial_outline)

            with gr.Row():
                # App name and explanation
                with gr.Column(elem_classes="app-header-col"):
                    gr.Markdown("# Document Generator")
                    gr.Markdown(" An AI tool for creating structured documents with customizable sections.")

                # Import and Save buttons
                with gr.Column():
                    with gr.Row(elem_classes="header-buttons-row"):
                        # Add empty space to push buttons to the right
                        gr.HTML("<div class='button-spacer' style='flex: 1;'></div>")
                        # Try Examples button with dropdown container
                        with gr.Column(elem_classes="try-examples-container"):
                            gr.Button(
                                "Template Examples",
                                elem_id="try-examples-btn-id",
                                variant="secondary",
                                size="sm",
                                elem_classes="try-examples-btn",
                            )
                            # Dropdown menu (hidden by default via CSS)
                            with gr.Column(elem_classes="examples-dropdown", elem_id="examples-dropdown-id"):
                                gr.HTML("""
                                    <div class="examples-dropdown-item" data-example="1">
                                        <div class="example-title">README</div>
                                        <div class="example-desc">Technical documentation with code</div>
                                    </div>
                                    <div class="examples-dropdown-item" data-example="2">
                                        <div class="example-title">Product Launch Documentation</div>
                                        <div class="example-desc">Product research and strategy</div>
                                    </div>
                                    <div class="examples-dropdown-item" data-example="3">
                                        <div class="example-title">Annual Performance Review</div>
                                        <div class="example-desc">Employee evaluation and feedback</div>
                                    </div>
                                """)
                        # New button (for resetting document)
                        new_doc_btn = gr.Button(
                            "New",
                            elem_id="new-builder-btn-id",
                            variant="secondary",
                            size="sm",
                            elem_classes="new-builder-btn",
                        )
                        gr.Button(
                            "Import",
                            elem_id="import-builder-btn-id",
                            variant="secondary",
                            size="sm",
                            elem_classes="import-builder-btn",
                        )
                        save_outline_btn = gr.DownloadButton(
                            "Save",
                            elem_id="save-builder-btn-id",
                            variant="secondary",
                            size="sm",
                            elem_classes="save-builder-btn",
                            visible=True,
                            value=create_docpack_from_current_state,
                        )

                    import_file = gr.File(
                        label="Import Docpack",
                        file_types=[".docpack"],
                        visible=True,
                        elem_id="import-file-input",
                        elem_classes="hidden-component",
                    )

            # Document title and description
            with gr.Row(elem_classes="header-section"):
                # Document title (narrower width)
                doc_title = gr.Textbox(
                    value="",
                    placeholder="Document Title",
                    label=None,
                    show_label=False,
                    elem_id="doc-title-id",
                    elem_classes="doc-title-box",
                    scale=2,
                    interactive=True,
                    lines=1,
                    max_lines=1,
                    visible=True,
                )

                # Document description (wider width)
                doc_description = gr.TextArea(
                    value="",
                    placeholder="Provide overall guidance for the document generation.\nSpecifics may include purpose, audience, style, format, etc.",
                    label=None,
                    show_label=False,
                    elem_id="doc-description-id",
                    elem_classes="doc-description-box",
                    scale=5,
                    lines=2,
                    max_lines=10,
                    interactive=True,
                    visible=True,
                )

            # Main content area with three columns
            with gr.Row():
                # Resources column: Upload Resources button
                with gr.Column(scale=1, elem_classes="resources-col"):
                    # Drag and drop file upload component
                    file_upload = gr.File(
                        label="Drop Text File Here",
                        file_count="multiple",
                        file_types=SUPPORTED_FILE_TYPES,
                        elem_classes="file-upload-dropzone",
                        visible=True,
                        height=90,
                        show_label=False,
                    )
                    
                    # Warning message for protected files - placed before the render area
                    file_upload_warning = gr.HTML(visible=False, elem_classes="file-upload-warning")

                    # Container for dynamic resource components
                    with gr.Column(elem_classes="resources-display-area"):

                        @gr.render(inputs=resources_state)
                        def render_resource_components(resources):
                            if not resources:
                                gr.HTML(
                                    value="<p style='color: #666; font-size: 12px'>(.docx, .md, .csv, .py, .json, .txt, etc.)</p>"
                                    "<p style='color: #666; font-size: 12px'>These reference files will be used for AI context.</p>"
                                )
                            else:
                                for idx, resource in enumerate(resources):
                                    with gr.Group(elem_classes="resource-item-gradio"):
                                        # Hidden element containing resource path for drag and drop
                                        gr.HTML(
                                            f'<div class="resource-path-hidden" style="display:none;" data-path="{resource["path"]}">{resource["path"]}</div>'
                                        )

                                        with gr.Row(elem_classes="resource-row-gradio"):
                                            with gr.Column(scale=1, elem_classes="resource-info-col"):
                                                # Resource title
                                                resource_title = gr.Textbox(
                                                    value=resource.get("title", resource["name"]),
                                                    placeholder="Title",
                                                    label=None,
                                                    show_label=False,
                                                    elem_classes="resource-title-gradio",
                                                    scale=1,
                                                )

                                                delete_btn = gr.Button(
                                                    "🗑", elem_classes="resource-delete-btn", size="sm"
                                                )

                                                # Resource description
                                                resource_desc = gr.Textbox(
                                                    value=resource.get("description", ""),
                                                    placeholder="Add a description for this resource...",
                                                    label=None,
                                                    show_label=False,
                                                    elem_classes="resource-desc-gradio",
                                                    lines=2,
                                                    scale=1,
                                                )

                                                # Filename display
                                                gr.HTML(
                                                    elem_classes="resource-filename",
                                                    value=f"<div>  {resource['name']}</div>",
                                                )

                                        # File replacement upload area
                                        replace_file = gr.File(
                                            label="Drop file here to replace",
                                            file_types=SUPPORTED_FILE_TYPES,
                                            elem_classes="resource-upload-gradio",
                                            scale=1,
                                            show_label=False,
                                        )
                                        
                                        # Warning message for protected files
                                        replace_warning = gr.HTML(visible=False)

                                        # Connect events for this resource
                                        resource_path = resource["path"]

                                        # Title update - don't update resources_state to avoid re-render
                                        resource_title.change(
                                            fn=update_resource_title_gradio,
                                            inputs=[
                                                resources_state,
                                                gr.State(resource_path),
                                                resource_title,
                                                doc_title,
                                                doc_description,
                                                blocks_state,
                                            ],
                                            outputs=[
                                                gr.State(),
                                                outline_state,
                                                json_output,
                                            ],  # Use dummy State to avoid re-render
                                            trigger_mode="always_last",  # Only trigger after user stops typing
                                        )

                                        # Description update - don't update resources_state to avoid re-render
                                        resource_desc.change(
                                            fn=update_resource_description_gradio,
                                            inputs=[
                                                resources_state,
                                                gr.State(resource_path),
                                                resource_desc,
                                                doc_title,
                                                doc_description,
                                                blocks_state,
                                            ],
                                            outputs=[
                                                gr.State(),
                                                outline_state,
                                                json_output,
                                            ],  # Use dummy State to avoid re-render
                                            trigger_mode="always_last",  # Only trigger after user stops typing
                                        )

                                        # Delete button
                                        def delete_gradio_and_render(resources, path, title, desc, blocks, focused):
                                            """Delete resource via Gradio button and render blocks."""
                                            print("\n=== delete_gradio_and_render called ===")
                                            new_res, new_blocks, outline, json_str = delete_resource_gradio(
                                                resources, path, title, desc, blocks
                                            )
                                            blocks_html = render_blocks(new_blocks, focused)
                                            print("=== delete_gradio_and_render complete ===\n")
                                            return new_res, new_blocks, outline, json_str, blocks_html

                                        delete_btn.click(
                                            fn=delete_gradio_and_render,
                                            inputs=[
                                                resources_state,
                                                gr.State(resource_path),
                                                doc_title,
                                                doc_description,
                                                blocks_state,
                                                focused_block_state,
                                            ],
                                            outputs=[
                                                resources_state,
                                                blocks_state,
                                                outline_state,
                                                json_output,
                                                blocks_display,
                                            ],
                                        )

                                        # File replacement
                                        replace_file.upload(
                                            fn=replace_resource_file_gradio,
                                            inputs=[
                                                resources_state,
                                                gr.State(resource_path),
                                                replace_file,
                                                doc_title,
                                                doc_description,
                                                blocks_state,
                                                session_state,
                                            ],
                                            outputs=[resources_state, outline_state, json_output, replace_file, replace_warning],
                                        ).then(
                                            # Force JSON update after resources render
                                            fn=lambda title, desc, res, blocks: regenerate_outline_from_state(
                                                title, desc, res, blocks
                                            )[1],
                                            inputs=[doc_title, doc_description, resources_state, blocks_state],
                                            outputs=[json_output],
                                        )

                # Workspace column: AI, H, T buttons (aligned left)
                with gr.Column(scale=1, elem_classes="workspace-col"):
                    with gr.Row(elem_classes="square-btn-row"):
                        ai_btn = gr.Button("+ Add Section", elem_classes="add-section-btn", size="sm")
                        # Add spacer to push collapse/expand buttons to the right
                        gr.HTML("<div style='flex: 1;'></div>")
                        # Collapse all button (same chevron as content blocks, rotated)
                        collapse_all_btn = gr.Button(
                            "⌵", 
                            elem_classes="collapse-all-btn workspace-collapse-btn",
                            elem_id="collapse-all-btn",
                            size="sm"
                        )
                        # Expand all button (same chevron as content blocks) 
                        expand_all_btn = gr.Button(
                            "⌵",
                            elem_classes="expand-all-btn workspace-collapse-btn", 
                            elem_id="expand-all-btn",
                            size="sm"
                        )

                    # Workspace panel for stacking content blocks
                    with gr.Column(elem_classes="workspace-display"):
                        blocks_display = gr.HTML(
                            value=render_blocks(initial_blocks, None), elem_classes="blocks-container"
                        )

                        # Hidden components for JS communication
                        delete_block_id = gr.Textbox(
                            visible=True, elem_id="delete-block-id", elem_classes="hidden-component"
                        )
                        delete_trigger = gr.Button(
                            "Delete", visible=True, elem_id="delete-trigger", elem_classes="hidden-component"
                        )

                        # Hidden HTML for JavaScript execution
                        gr.HTML(visible=False)

                        # Hidden components for content updates
                        update_block_id = gr.Textbox(
                            visible=True, elem_id="update-block-id", elem_classes="hidden-component"
                        )
                        update_content_input = gr.Textbox(
                            visible=True, elem_id="update-content-input", elem_classes="hidden-component"
                        )
                        update_trigger = gr.Button(
                            "Update", visible=True, elem_id="update-trigger", elem_classes="hidden-component"
                        )

                        # Hidden components for resource deletion
                        delete_resource_path = gr.Textbox(
                            visible=True, elem_id="delete-resource-path", elem_classes="hidden-component"
                        )
                        delete_resource_trigger = gr.Button(
                            "Delete Resource",
                            visible=True,
                            elem_id="delete-resource-trigger",
                            elem_classes="hidden-component",
                        )

                        # Hidden components for toggle collapse
                        toggle_block_id = gr.Textbox(
                            visible=True, elem_id="toggle-block-id", elem_classes="hidden-component"
                        )
                        toggle_trigger = gr.Button(
                            "Toggle", visible=True, elem_id="toggle-trigger", elem_classes="hidden-component"
                        )

                        # Hidden components for heading updates
                        update_heading_block_id = gr.Textbox(
                            visible=True, elem_id="update-heading-block-id", elem_classes="hidden-component"
                        )
                        update_heading_input = gr.Textbox(
                            visible=True, elem_id="update-heading-input", elem_classes="hidden-component"
                        )
                        update_heading_trigger = gr.Button(
                            "Update Heading",
                            visible=True,
                            elem_id="update-heading-trigger",
                            elem_classes="hidden-component",
                        )

                        # Hidden components for indent updates
                        indent_block_id = gr.Textbox(
                            visible=True, elem_id="indent-block-id", elem_classes="hidden-component"
                        )
                        indent_direction = gr.Textbox(
                            visible=True, elem_id="indent-direction", elem_classes="hidden-component"
                        )
                        indent_trigger = gr.Button(
                            "Update Indent", visible=True, elem_id="indent-trigger", elem_classes="hidden-component"
                        )

                        # Hidden components for focus tracking
                        focus_block_id = gr.Textbox(
                            visible=True, elem_id="focus-block-id", elem_classes="hidden-component"
                        )
                        focus_trigger = gr.Button(
                            "Set Focus", visible=True, elem_id="focus-trigger", elem_classes="hidden-component"
                        )

                        # Hidden components for adding block after
                        add_after_block_id = gr.Textbox(
                            visible=True, elem_id="add-after-block-id", elem_classes="hidden-component"
                        )
                        add_after_type = gr.Textbox(
                            visible=True, elem_id="add-after-type", elem_classes="hidden-component"
                        )
                        add_after_trigger = gr.Button(
                            "Add After", visible=True, elem_id="add-after-trigger", elem_classes="hidden-component"
                        )

                        # Hidden components for converting block type
                        convert_block_id = gr.Textbox(
                            visible=True, elem_id="convert-block-id", elem_classes="hidden-component"
                        )
                        convert_type = gr.Textbox(visible=True, elem_id="convert-type", elem_classes="hidden-component")
                        convert_trigger = gr.Button(
                            "Convert", visible=True, elem_id="convert-trigger", elem_classes="hidden-component"
                        )

                        # Hidden components for updating block resources
                        update_resources_block_id = gr.Textbox(
                            visible=True, elem_id="update-resources-block-id", elem_classes="hidden-component"
                        )
                        update_resources_input = gr.Textbox(
                            visible=True, elem_id="update-resources-input", elem_classes="hidden-component"
                        )
                        update_resources_trigger = gr.Button(
                            "Update Resources",
                            visible=True,
                            elem_id="update-resources-trigger",
                            elem_classes="hidden-component",
                        )

                        # Hidden components for removing block resources
                        remove_resource_block_id = gr.Textbox(
                            visible=True, elem_id="remove-resource-block-id", elem_classes="hidden-component"
                        )
                        remove_resource_path = gr.Textbox(
                            visible=True, elem_id="remove-resource-path", elem_classes="hidden-component"
                        )
                        remove_resource_trigger = gr.Button(
                            "Remove Resource",
                            visible=True,
                            elem_id="remove-resource-trigger",
                            elem_classes="hidden-component",
                        )

                        # Hidden components for deleting resources from panel
                        delete_panel_resource_path = gr.Textbox(visible=False, elem_id="delete-panel-resource-path")
                        delete_panel_resource_trigger = gr.Button(
                            "Delete Panel Resource", visible=False, elem_id="delete-panel-resource-trigger"
                        )

                        # Hidden components for updating resource descriptions
                        update_desc_block_id = gr.Textbox(visible=False, elem_id="update-desc-block-id")
                        update_desc_resource_path = gr.Textbox(visible=False, elem_id="update-desc-resource-path")
                        update_desc_text = gr.Textbox(visible=False, elem_id="update-desc-text")
                        update_desc_trigger = gr.Button(
                            "Update Description", visible=False, elem_id="update-desc-trigger"
                        )

                        # Hidden components for loading examples
                        example_id_input = gr.Textbox(  # this shows up as textarea locally but as input deployed
                            visible=True, elem_id="example-id-input", elem_classes="hidden-component"
                        )
                        load_example_trigger = gr.Button(
                            "Load Example",
                            visible=True,
                            elem_id="load-example-trigger",
                            elem_classes="hidden-component",
                        )

                        # Hidden components for updating resource titles
                        update_title_resource_path = gr.Textbox(visible=False, elem_id="update-title-resource-path")
                        update_title_text = gr.Textbox(visible=False, elem_id="update-title-text")
                        update_title_trigger = gr.Button("Update Title", visible=False, elem_id="update-title-trigger")

                        # Hidden button for updating resource panel descriptions
                        update_panel_desc_trigger = gr.Button(
                            "Update Panel Description", visible=False, elem_id="update-panel-desc-trigger"
                        )

                        # Hidden components for replacing resource files
                        replace_resource_path = gr.Textbox(visible=False, elem_id="replace-resource-path")
                        replace_resource_file_input = gr.File(
                            visible=False,
                            elem_id="replace-resource-file",
                            file_types=SUPPORTED_FILE_TYPES,
                        )
                        replace_resource_trigger = gr.Button(
                            "Replace Resource", visible=False, elem_id="replace-resource-trigger"
                        )
                        replace_success_msg = gr.Textbox(visible=False, elem_id="replace-success-msg")

                # Generated document column: Generate and Save Document buttons (aligned right)
                with gr.Column(scale=1, elem_classes="generate-col"):
                    with gr.Row(elem_classes="generate-btn-row"):
                        # Add empty space to push buttons to the right
                        gr.HTML("<div style='flex: 1;'></div>")
                        generate_doc_btn = gr.Button(
                            "▷ Generate", elem_classes="generate-btn", variant="primary", size="sm"
                        )
                        save_doc_btn = gr.DownloadButton(
                            "Download",
                            elem_classes="download-btn",
                            variant="secondary",
                            size="sm",
                            visible=True,
                            interactive=False,  # Disabled until document is generated
                        )

                    # Generated document display panel
                    with gr.Column(elem_classes="generate-display"):
                        generated_content_html = gr.HTML(
                            value="<em>Click '▷ Generate' to see the generated content here.</em><br><br><br>",
                            elem_classes="generated-content",
                            visible=True,
                        )
                        generated_content = gr.Markdown(visible=False)

                    # Debug panel for JSON display (collapsible)
                    with gr.Column(elem_classes="debug-panel", elem_id="debug-panel-container"):
                        with gr.Row(elem_classes="debug-panel-header"):
                            gr.HTML("""
                                <div class="debug-panel-title" onclick="toggleDebugPanel()">
                                    <span>Debug Panel (JSON Output)</span>
                                    <span class="debug-collapse-icon" id="debug-collapse-icon">⌵</span>
                                </div>
                            """)

                        with gr.Column(elem_classes="debug-panel-content", elem_id="debug-panel-content", visible=True):
                            json_output = gr.Code(
                                value=initial_json,
                                language="json",
                                elem_classes="json-debug-output",
                                wrap_lines=True,
                                lines=20,
                            )

        # Helper function to add AI block and regenerate outline
        def handle_add_ai_block_top(blocks, _, title, description, resources):
            blocks = add_ai_block(blocks, None)
            outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
            return blocks, outline, json_str

        # Helper function to add Text block and regenerate outline
        def handle_add_text_block_top(blocks, _, title, description, resources):
            blocks = add_text_block(blocks, None)
            outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
            return blocks, outline, json_str
        
        # Helper function to collapse all blocks
        def collapse_all_blocks(blocks):
            for block in blocks:
                block["collapsed"] = True
            return blocks
        
        # Helper function to expand all blocks  
        def expand_all_blocks(blocks):
            for block in blocks:
                block["collapsed"] = False
            return blocks

        # Connect button click to add AI block
        ai_btn.click(
            fn=handle_add_ai_block_top,
            inputs=[
                blocks_state,
                gr.State(None),
                doc_title,
                doc_description,
                resources_state,
            ],  # Always pass None for focused_block_id
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)
        
        # Connect collapse all button
        collapse_all_btn.click(
            fn=collapse_all_blocks,
            inputs=[blocks_state],
            outputs=[blocks_state]
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)
        
        # Connect expand all button
        expand_all_btn.click(
            fn=expand_all_blocks,
            inputs=[blocks_state],
            outputs=[blocks_state]
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Connect button click to add Text block

        # Delete block handler
        delete_trigger.click(
            fn=delete_block,
            inputs=[blocks_state, delete_block_id, doc_title, doc_description, resources_state],
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Delete resource handler
        delete_resource_trigger.click(
            fn=delete_resource_gradio,
            inputs=[resources_state, delete_resource_path, doc_title, doc_description, blocks_state],
            outputs=[resources_state, blocks_state, outline_state, json_output],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Update block content handler
        update_trigger.click(
            fn=update_block_content,
            inputs=[blocks_state, update_block_id, update_content_input, doc_title, doc_description, resources_state],
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=set_focused_block, inputs=update_block_id, outputs=focused_block_state)

        # Toggle collapse handler
        toggle_trigger.click(
            fn=toggle_block_collapse, inputs=[blocks_state, toggle_block_id], outputs=blocks_state
        ).then(fn=set_focused_block, inputs=toggle_block_id, outputs=focused_block_state).then(
            fn=render_blocks, inputs=[blocks_state, toggle_block_id], outputs=blocks_display
        )

        # Update heading handler
        update_heading_trigger.click(
            fn=update_block_heading,
            inputs=[
                blocks_state,
                update_heading_block_id,
                update_heading_input,
                doc_title,
                doc_description,
                resources_state,
            ],
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=set_focused_block, inputs=update_heading_block_id, outputs=focused_block_state)

        # Update indent handler
        indent_trigger.click(
            fn=update_block_indent,
            inputs=[blocks_state, indent_block_id, indent_direction, doc_title, doc_description, resources_state],
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display).then(
            fn=set_focused_block, inputs=indent_block_id, outputs=focused_block_state
        )

        # Focus handler
        focus_trigger.click(fn=set_focused_block, inputs=focus_block_id, outputs=focused_block_state).then(
            fn=render_blocks, inputs=[blocks_state, focus_block_id], outputs=blocks_display
        )

        # Add after handler - for + button on content blocks
        def handle_add_after(blocks, block_id, block_type, title, description, resources):
            if block_type == "ai":
                blocks = add_ai_block(blocks, block_id)
            else:
                blocks = add_text_block(blocks, block_id)

            # Regenerate outline and JSON
            outline, json_str = regenerate_outline_from_state(title, description, resources, blocks)
            return blocks, outline, json_str

        add_after_trigger.click(
            fn=handle_add_after,
            inputs=[blocks_state, add_after_block_id, add_after_type, doc_title, doc_description, resources_state],
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Convert block type handler
        convert_trigger.click(
            fn=convert_block_type,
            inputs=[blocks_state, convert_block_id, convert_type, doc_title, doc_description, resources_state],
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Update block resources handler
        update_resources_trigger.click(
            fn=update_block_resources,
            inputs=[
                blocks_state,
                update_resources_block_id,
                update_resources_input,
                doc_title,
                doc_description,
                resources_state,
            ],
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Remove block resource handler
        remove_resource_trigger.click(
            fn=remove_block_resource,
            inputs=[
                blocks_state,
                remove_resource_block_id,
                remove_resource_path,
                doc_title,
                doc_description,
                resources_state,
            ],
            outputs=[blocks_state, outline_state, json_output],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Delete resource from panel handler
        def delete_and_render(resources, resource_path, title, description, blocks, focused_id):
            """Delete resource and return both the state updates and rendered HTML."""
            print("\n=== delete_and_render called ===")
            print(f"Resource path: {resource_path}")
            print(f"Blocks before: {len(blocks)} blocks")

            new_resources, updated_blocks, outline, json_str = delete_resource_from_panel(
                resources, resource_path, title, description, blocks
            )

            print(f"Blocks after delete: {len(updated_blocks)} blocks")

            # Render the blocks immediately
            blocks_html = render_blocks(updated_blocks, focused_id)

            print(f"Generated HTML length: {len(blocks_html)}")
            print("=== delete_and_render complete ===\n")

            return new_resources, updated_blocks, outline, json_str, blocks_html

        delete_panel_resource_trigger.click(
            fn=delete_and_render,
            inputs=[
                resources_state,
                delete_panel_resource_path,
                doc_title,
                doc_description,
                blocks_state,
                focused_block_state,
            ],
            outputs=[resources_state, blocks_state, outline_state, json_output, blocks_display],
        )

        # Update resource description handler - don't re-render blocks to avoid interrupting typing
        update_desc_trigger.click(
            fn=update_resource_description,
            inputs=[
                blocks_state,
                update_desc_block_id,
                update_desc_resource_path,
                update_desc_text,
                doc_title,
                doc_description,
                resources_state,
            ],
            outputs=[blocks_state, outline_state, json_output],
        )

        # Title and description change handlers
        doc_title.change(
            fn=update_document_metadata,
            inputs=[doc_title, doc_description, resources_state, blocks_state],
            outputs=[outline_state, json_output],
        )

        doc_description.change(
            fn=update_document_metadata,
            inputs=[doc_title, doc_description, resources_state, blocks_state],
            outputs=[outline_state, json_output],
        )

        # Handle file uploads (defined after json_output is created)
        file_upload.upload(
            fn=handle_file_upload,
            inputs=[file_upload, resources_state, doc_title, doc_description, blocks_state, session_state],
            outputs=[resources_state, file_upload, outline_state, json_output, session_state, file_upload_warning],
        ).then(
            # Force JSON update after resources render
            fn=lambda title, desc, res, blocks: regenerate_outline_from_state(title, desc, res, blocks)[1],
            inputs=[doc_title, doc_description, resources_state, blocks_state],
            outputs=[json_output],
        )

        # Generate document handler - update to return the download button state
        async def handle_generate_and_update_download(title, description, resources, blocks, session_id):
            """Generate document and update download button."""
            json_str, content, file_path, filename = await handle_document_generation(
                title, description, resources, blocks, session_id
            )

            # Hide HTML component and show Markdown component
            html_update = gr.update(visible=False)
            markdown_update = gr.update(value=content, visible=True)

            if file_path:
                download_update = gr.update(value=file_path, interactive=True)
            else:
                download_update = gr.update(interactive=False)

            # Re-enable the generate button
            generate_btn_update = gr.update(interactive=True)

            return json_str, markdown_update, html_update, download_update, generate_btn_update

        generate_doc_btn.click(
            fn=lambda: [
                gr.update(interactive=False),  # Disable generate button
                gr.update(visible=False),  # Hide markdown content
                gr.update(
                    value="<em></em><br><br><br>", visible=True
                ),  # Show HTML with empty content but structure intact
                gr.update(interactive=False),  # Disable download button
            ],
            outputs=[generate_doc_btn, generated_content, generated_content_html, save_doc_btn],
        ).then(
            fn=handle_generate_and_update_download,
            inputs=[doc_title, doc_description, resources_state, blocks_state, session_state],
            outputs=[json_output, generated_content, generated_content_html, save_doc_btn, generate_doc_btn],
        )

        # Save button is handled directly by DownloadButton with create_docpack_from_current_state

        # Import file handler
        import_file.change(
            fn=import_outline,
            inputs=[import_file, session_state],
            outputs=[
                doc_title,
                doc_description,
                resources_state,
                blocks_state,
                outline_state,
                json_output,
                import_file,  # Add import_file to outputs to clear it
                session_state,
                generated_content_html,
                generated_content,
                save_doc_btn,
            ],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Update save button value whenever outline changes
        outline_state.change(fn=lambda: gr.update(value=create_docpack_from_current_state()), outputs=save_outline_btn)

        # Load example handler
        load_example_trigger.click(
            fn=load_example,
            inputs=[example_id_input, session_state],
            outputs=[
                doc_title,
                doc_description,
                resources_state,
                blocks_state,
                outline_state,
                json_output,
                session_state,
                generated_content_html,
                generated_content,
                save_doc_btn,
            ],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Update resource title handler - don't re-render resources to avoid interrupting typing
        update_title_trigger.click(
            fn=update_resource_title,
            inputs=[
                resources_state,
                update_title_resource_path,
                update_title_text,
                doc_title,
                doc_description,
                blocks_state,
            ],
            outputs=[resources_state, outline_state, json_output],
        )

        # Update resource panel description handler - reuse the same inputs
        update_panel_desc_trigger.click(
            fn=update_resource_panel_description,
            inputs=[
                resources_state,
                update_title_resource_path,
                update_title_text,
                doc_title,
                doc_description,
                blocks_state,
            ],
            outputs=[resources_state, outline_state, json_output],
        )

        # Replace resource file handler
        def handle_resource_replacement(resources, old_path, new_file, doc_title, doc_description, blocks, session_id):
            """Handle resource file replacement."""
            if not new_file:
                # No file selected, return unchanged - regenerate outline to return current state
                outline, json_str = regenerate_outline_from_state(doc_title, doc_description, resources, blocks)
                return resources, blocks, outline, json_str, ""

            # new_file is the file path from Gradio
            new_file_path = new_file if isinstance(new_file, str) else new_file.name

            # Call the replace function
            updated_resources, updated_blocks, resources_html, outline, json_str, success_msg = replace_resource_file(
                resources, old_path, new_file_path, doc_title, doc_description, blocks, session_id
            )

            # Return only the values that match the outputs list
            return updated_resources, updated_blocks, outline, json_str, success_msg

        replace_resource_trigger.click(
            fn=handle_resource_replacement,
            inputs=[
                resources_state,
                replace_resource_path,
                replace_resource_file_input,
                doc_title,
                doc_description,
                blocks_state,
                session_state,
            ],
            outputs=[
                resources_state,
                blocks_state,
                outline_state,
                json_output,
                replace_success_msg,
            ],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display).then(
            # Clear the file input after processing
            fn=lambda: None,
            outputs=replace_resource_file_input,
        )

        # New button - reset document to initial state
        def reset_document():
            """Reset document to initial state with new session."""
            # Create fresh initial blocks with new IDs
            new_blocks = [
                {
                    "id": str(uuid.uuid4()),
                    "type": "ai",
                    "heading": "",
                    "content": "",
                    "resources": [],
                    "collapsed": False,
                    "indent_level": 0,
                },
                {
                    "id": str(uuid.uuid4()),
                    "type": "text",
                    "heading": "",
                    "content": "",
                    "resources": [],
                    "collapsed": True,
                    "indent_level": 0,
                },
            ]

            # Generate initial outline
            initial_outline, initial_json = regenerate_outline_from_state("", "", [], new_blocks)

            # New session ID
            new_session_id = str(uuid.uuid4())

            # Return updates for all relevant components
            return (
                "",  # doc_title
                "",  # doc_description
                [],  # resources_state
                new_blocks,  # blocks_state
                initial_outline,  # outline_state
                initial_json,  # json_output
                new_session_id,  # session_state
                gr.update(value="", visible=False),  # generated_content_html
                gr.update(value="", visible=False),  # generated_content
                gr.update(interactive=False),  # save_doc_btn
                None,  # focused_block_state
            )

        new_doc_btn.click(
            fn=reset_document,
            outputs=[
                doc_title,
                doc_description,
                resources_state,
                blocks_state,
                outline_state,
                json_output,
                session_state,
                generated_content_html,
                generated_content,
                save_doc_btn,
                focused_block_state,
            ],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display)

        # Create a hidden HTML component for tab switching trigger
        switch_tab_trigger = gr.HTML("", visible=True, elem_id="switch-tab-trigger", elem_classes="hidden-component")

        # Get Started button - generate docpack and switch to Draft + Generate tab

        # Add event handlers for the Draft button
        def check_prompt_before_submit(prompt):
            """Check if prompt exists and show error if not."""
            if not prompt or not prompt.strip():
                # Show error message, hide loading, enable button
                return (
                    gr.update(
                        value='''<div id="prompt_error" style="position: relative; color: #dc2626; padding: 8px 30px 8px 12px; background: #fee2e2; border-radius: 4px; margin-top: 8px; font-size: 14px;">
                            <button onclick="document.getElementById('prompt_error').style.display='none'" 
                                    style="position: absolute; top: 4px; right: 5px; background: none; border: none; color: #dc2626; font-size: 18px; cursor: pointer; padding: 0 5px; opacity: 0.6;" 
                                    onmouseover="this.style.opacity='1'" 
                                    onmouseout="this.style.opacity='0.6'"
                                    title="Close">×</button>
                            Please enter a description of what you'd like to create.
                        </div>''',
                        visible=True,
                    ),
                    gr.update(interactive=True),  # Enable button
                )
            else:
                # Hide error message, show loading, disable button
                return (
                    gr.update(visible=False),
                    gr.update(interactive=True),  # Keep button enabled
                )

        get_started_btn.click(
            fn=check_prompt_before_submit,
            inputs=[start_prompt_input],
            outputs=[start_error_message, get_started_btn],
            queue=False,  # Run immediately
        ).success(
            fn=handle_start_draft_click,
            inputs=[start_prompt_input, start_resources_state, session_state],
            outputs=[
                doc_title,
                doc_description,
                resources_state,
                blocks_state,
                outline_state,
                json_output,
                session_state,
                generated_content_html,
                generated_content,
                save_doc_btn,
                switch_tab_trigger,
                start_error_message,
                start_prompt_input,
                get_started_btn,
            ],
        ).then(fn=render_blocks, inputs=[blocks_state, focused_block_state], outputs=blocks_display).then(
            fn=regenerate_outline_from_state,
            inputs=[doc_title, doc_description, resources_state, blocks_state],
            outputs=[outline_state, json_output],
        )

        # Wrapper for file upload that includes rendering
        def handle_start_file_upload_with_render(files, current_resources):
            """Handle file uploads and render the resources."""
            new_resources, clear_upload, warning_update = handle_start_file_upload(files, current_resources)
            resources_html = render_start_resources(new_resources)
            return new_resources, clear_upload, resources_html, warning_update

        # Start tab file upload handler
        start_file_upload.upload(
            fn=handle_start_file_upload_with_render,
            inputs=[start_file_upload, start_resources_state],
            outputs=[start_resources_state, start_file_upload, start_resources_display, start_upload_warning],
        )

        # Clear error message when user starts typing
        start_prompt_input.input(fn=lambda: gr.update(visible=False), outputs=[start_error_message], queue=False)

        # Example button handlers
        def extract_resources_from_docpack(docpack_path, session_id=None):
            """Extract resources from a docpack file."""
            # Define allowed extensions for start tab (same as file upload)
            ALLOWED_EXTENSIONS = {
                ".txt",
                ".md",
                ".py",
                ".c",
                ".cpp",
                ".h",
                ".java",
                ".js",
                ".ts",
                ".jsx",
                ".tsx",
                ".json",
                ".xml",
                ".yaml",
                ".yml",
                ".toml",
                ".ini",
                ".cfg",
                ".conf",
                ".sh",
                ".bash",
                ".zsh",
                ".fish",
                ".ps1",
                ".bat",
                ".cmd",
                ".rs",
                ".go",
                ".rb",
                ".php",
                ".pl",
                ".lua",
                ".r",
                ".m",
                ".swift",
                ".kt",
                ".scala",
                ".clj",
                ".ex",
                ".erl",
                ".hs",
                ".ml",
                ".fs",
                ".nim",
                ".d",
                ".dart",
                ".jl",
                ".v",
                ".zig",
                ".html",
                ".htm",
                ".css",
                ".scss",
                ".sass",
                ".less",
                ".vue",
                ".svelte",
                ".astro",
                ".tex",
                ".rst",
                ".adoc",
                ".org",
                ".csv",
            }

            resources = []
            if docpack_path.exists():
                print(f"DEBUG: Docpack exists at {docpack_path}")
                try:
                    # Use provided session ID or create a new one
                    if not session_id:
                        session_id = str(uuid.uuid4())
                        print(f"DEBUG: Created new session ID: {session_id}")
                    else:
                        print(f"DEBUG: Using existing session ID: {session_id}")

                    # Create a temporary directory for extraction
                    with tempfile.TemporaryDirectory() as temp_dir:
                        print(f"DEBUG: Created temp directory: {temp_dir}")
                        # Extract the docpack - convert temp_dir to Path object
                        print(f"DEBUG: Extracting docpack from {docpack_path} to {temp_dir}")
                        json_data, extracted_files = DocpackHandler.extract_package(str(docpack_path), Path(temp_dir))
                        print(f"DEBUG: Extraction successful. Found {len(extracted_files)} files")
                        print(f"DEBUG: JSON data has {len(json_data.get('resources', []))} resources")

                        # Process resources from the docpack
                        for res_data in json_data.get("resources", []):
                            # Skip inline resources
                            if res_data.get("is_inline", False) or res_data.get("key", "").startswith(
                                "inline_resource_"
                            ):
                                continue

                            # Get the actual file from extracted files
                            resource_filename = Path(res_data.get("path", "")).name
                            file_ext = Path(resource_filename).suffix.lower()

                            # Check if file extension is allowed
                            if file_ext not in ALLOWED_EXTENSIONS:
                                continue

                            for extracted_file in extracted_files:
                                if Path(extracted_file).name == resource_filename:
                                    # Read the file content
                                    with open(extracted_file, "r", encoding="utf-8") as f:
                                        content = f.read()

                                    # Use the session ID created at the beginning
                                    session_dir = session_manager.get_session_dir(session_id)

                                    # Convert Path to string for os.path operations
                                    session_dir_str = str(session_dir)

                                    # Save the file to session directory
                                    files_dir = os.path.join(session_dir_str, "files")
                                    os.makedirs(files_dir, exist_ok=True)
                                    target_path = os.path.join(files_dir, resource_filename)
                                    with open(target_path, "w", encoding="utf-8") as f:
                                        f.write(content)

                                    # Calculate file size
                                    file_size = len(content.encode("utf-8"))
                                    if file_size < 1024:
                                        size_str = f"{file_size} B"
                                    elif file_size < 1024 * 1024:
                                        size_str = f"{file_size / 1024:.1f} KB"
                                    else:
                                        size_str = f"{file_size / (1024 * 1024):.1f} MB"

                                    # Use the same format as handle_start_file_upload
                                    resources.append({
                                        "path": target_path,
                                        "name": resource_filename,
                                        "size": size_str,
                                    })
                                    break
                except Exception as e:
                    print(f"Error extracting resources from docpack: {e}")

            print(f"DEBUG extract_resources_from_docpack: Returning {len(resources)} resources")
            for r in resources:
                print(f"  Resource: {r}")
            return resources

        def load_code_readme_example(session_id):
            """Load the code README example prompt and resources."""
            # Get or create session
            if not session_id:
                session_id = str(uuid.uuid4())

            prompt = "Generate a comprehensive production-ready README for the target codebase. Include key features, installation instructions, usage examples, API documentation, an architecture overview, and contribution guidelines. IMPORTANT to use ONLY the facts available in the referenced documents (code, configs, docs, tests, etc.). Keep prose short, use bullet lists when helpful, and prefer plan language over marketing fluff.  Assumer the audience is a developer seeing the project for the first time."

            # Extract resources from the README docpack
            examples_dir = Path(__file__).parent.parent / "examples"
            docpack_path = examples_dir / "readme-generation" / "readme.docpack"
            resources = extract_resources_from_docpack(docpack_path, session_id)

            print(f"DEBUG: Loaded {len(resources)} resources for README example")
            for r in resources:
                print(f"  - {r['name']} ({r['size']})")

            # Render the resources HTML
            resources_html = render_start_resources(resources)

            return prompt, resources, session_id, resources_html

        def load_product_launch_example(session_id):
            """Load the product launch example prompt and resources."""
            # Get or create session
            if not session_id:
                session_id = str(uuid.uuid4())

            prompt = "Create a comprehensive product launch documentation package for a new B2B SaaS analytics product.  Include the value proposition, implementation details and customer benefits.  There should be a product over section, one on technical architecture, an implementation guide, pricing and packaging, and go-to market strategy.  Other areas to consider include an announcement blog post, press release, internal team briefing, and customer FAQ.  Be sure to use clear, professional language appropriate for both technical and business stakeholders."

            # Extract resources from the product launch docpack
            examples_dir = Path(__file__).parent.parent / "examples"
            docpack_path = examples_dir / "launch-documentation" / "launch-documentation.docpack"
            resources = extract_resources_from_docpack(docpack_path, session_id)

            # Render the resources HTML
            resources_html = render_start_resources(resources)

            return prompt, resources, session_id, resources_html

        def load_performance_review_example(session_id):
            """Load the performance review example prompt and resources."""
            # Get or create session
            if not session_id:
                session_id = str(uuid.uuid4())

            prompt = "Generate an annual performance review for an employee. It will be used by both the manager and the employee to discuss the employee's progress.  Include key achievements, areas for growth, training and development and next years goals.  Make sure there is an employee overview as well.  Make it constructive and motivating, but also concise.  Folks are busy."

            # Extract resources from the performance review docpack
            examples_dir = Path(__file__).parent.parent / "examples"
            docpack_path = (
                examples_dir
                / "scenario-4-annual-performance-review"
                / "Annual Employee Performance Review_20250709_153352.docpack"
            )
            resources = extract_resources_from_docpack(docpack_path, session_id)

            # Render the resources HTML
            resources_html = render_start_resources(resources)

            return prompt, resources, session_id, resources_html

        example_code_readme_btn.click(
            fn=load_code_readme_example,
            inputs=[session_state],
            outputs=[start_prompt_input, start_resources_state, session_state, start_resources_display],
            queue=False,
        )

        example_product_launch_btn.click(
            fn=load_product_launch_example,
            inputs=[session_state],
            outputs=[start_prompt_input, start_resources_state, session_state, start_resources_display],
            queue=False,
        )

        example_performance_review_btn.click(
            fn=load_performance_review_example,
            inputs=[session_state],
            outputs=[start_prompt_input, start_resources_state, session_state, start_resources_display],
            queue=False,
        )

        # Hidden inputs for Start tab resource removal
        start_remove_resource_index = gr.Textbox(
            elem_id="start-remove-resource-index", visible=True, elem_classes="hidden-component"
        )
        start_remove_resource_name = gr.Textbox(
            elem_id="start-remove-resource-name", visible=True, elem_classes="hidden-component"
        )
        start_remove_resource_btn = gr.Button(
            "Remove", elem_id="start-remove-resource-btn", visible=True, elem_classes="hidden-component"
        )

        # Function to remove resource from Start tab
        def remove_start_resource(resources, index_str, name):
            """Remove a resource from the Start tab by index."""
            print(
                f"DEBUG: remove_start_resource called with resources={len(resources) if resources else 0}, index_str='{index_str}', name='{name}'"
            )

            if not resources or not index_str:
                print("DEBUG: Early return - no resources or no index_str")
                resources_html = render_start_resources(resources)
                return resources, resources_html

            try:
                index = int(index_str)
                print(f"DEBUG: Parsed index={index}, resources length={len(resources)}")

                if 0 <= index < len(resources):
                    print(f"DEBUG: Index is valid. Resource at index: {resources[index].get('name', 'unknown')}")

                    # Verify the name matches as a safety check
                    if resources[index]["name"] == name:
                        print(f"DEBUG: Name matches, removing resource at index {index}")
                        new_resources = resources.copy()
                        removed_resource = new_resources.pop(index)
                        print(f"DEBUG: Removed resource: {removed_resource}")
                        resources_html = render_start_resources(new_resources)
                        print(f"DEBUG: Successfully removed resource, new count: {len(new_resources)}")
                        return new_resources, resources_html
                    else:
                        print(f"DEBUG: Name mismatch - expected '{name}', got '{resources[index]['name']}'")
                else:
                    print(f"DEBUG: Index {index} out of range for {len(resources)} resources")
            except (ValueError, IndexError) as e:
                print(f"DEBUG: Exception in remove_start_resource: {e}")

            print("DEBUG: No changes made, returning original resources")
            resources_html = render_start_resources(resources)
            return resources, resources_html

        # Start tab resource removal handler
        start_remove_resource_btn.click(
            fn=remove_start_resource,
            inputs=[start_resources_state, start_remove_resource_index, start_remove_resource_name],
            outputs=[start_resources_state, start_resources_display],
        )

    return app


def check_deployment_status():
    """Quick deployment status check."""
    # Verify essential configuration
    app_root = Path(__file__).resolve().parents[1]
    bundled_recipe_path = app_root / "document_generator_app" / "recipes" / "document_generator_recipe.json"

    print("Document Generator starting...")
    print(f"Recipe source: {'bundled' if bundled_recipe_path.exists() else 'development'}")

    # Show LLM provider configuration
    provider = os.getenv("LLM_PROVIDER", "openai")
    model = os.getenv("DEFAULT_MODEL", "gpt-4o")
    print(f"LLM: {provider}/{model}")


def main():
    """Main entry point for the Document Builder app."""
    global IS_DEV_MODE

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Document Generator App")
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    args = parser.parse_args()

    # Set global dev mode variable
    IS_DEV_MODE = args.dev

    # Load environment variables from .env file
    load_dotenv()

    # Run diagnostic check
    check_deployment_status()

    # Configuration for hosting - Azure App Service uses PORT environment variable
    if args.dev:
        print("Running in DEVELOPMENT mode")

    # Production mode settings
    server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    server_port = int(os.getenv("PORT", os.getenv("GRADIO_SERVER_PORT", "8000")))

    print(f"Server: {server_name}:{server_port}")

    app = create_app()

    import logging

    if args.dev:
        logging.basicConfig(level=logging.DEBUG)
        app.launch(server_name=server_name, server_port=server_port, mcp_server=True, pwa=True, share=False)
    else:
        logging.basicConfig(level=logging.INFO)
        app.launch(server_name=server_name, server_port=server_port, mcp_server=True, pwa=True)


if __name__ == "__main__":
    main()


=== File: apps/document-generator/document_generator_app/config.py ===
"""Configuration settings for the Document Generator V2 app."""

import os
from typing import NamedTuple, List


class ExampleOutline(NamedTuple):
    """Configuration for an example document outline."""

    name: str
    path: str


class Settings:
    """Configuration settings for the Document Generator app."""

    # App settings
    app_title: str = "Document Generator"
    app_description: str = "Create structured documents with AI assistance"

    # LLM Configuration
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")  # "openai" or "azure"
    default_model: str = os.getenv("DEFAULT_MODEL", "gpt-4o")

    @property
    def model_id(self) -> str:
        """Get the full model ID for recipe-executor."""
        return f"{self.llm_provider}/{self.default_model}"

    # Example outlines
    example_outlines: List[ExampleOutline] = [
        ExampleOutline(
            name="README Generator",
            path="examples/readme-generation/readme.docpack",
        ),
        ExampleOutline(
            name="Product Launch Documentation",
            path="examples/launch-documentation/launch-documentation.docpack",
        ),
        ExampleOutline(
            name="Annual Performance Review",
            path="examples/scenario-4-annual-performance-review/Annual Employee Performance Review_20250701_133228.docpack",
        ),
    ]


# Create global settings instance
settings = Settings()


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
import logging
import os
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from recipe_executor.config import load_configuration
from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger

from ..config import settings
from ..models.outline import Outline, Resource
from ..resource_resolver import resolve_all_resources
from ..session import session_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_document(
    outline: Optional[Outline], session_id: Optional[str] = None, dev_mode: bool = False
) -> str:
    """
    Run the document-generator recipe with the given outline and return the generated Markdown.
    """
    logger.info(f"Starting document generation for session: {session_id}")
    logger.info(f"Running in {'development' if dev_mode else 'production'} mode")

    # Allow stub invocation without an outline for initial tests
    if outline is None:
        logger.warning("No outline provided, returning empty document")
        return ""

    # First try bundled recipes (for deployment), then fall back to repo structure (for development)
    APP_ROOT = Path(__file__).resolve().parents[2]  # document_generator_app parent
    BUNDLED_RECIPE_PATH = APP_ROOT / "document_generator_app" / "recipes" / "document_generator_recipe.json"

    logger.info(f"APP_ROOT: {APP_ROOT}")
    logger.info(f"BUNDLED_RECIPE_PATH: {BUNDLED_RECIPE_PATH}")
    logger.info(f"Bundled recipe exists: {BUNDLED_RECIPE_PATH.exists()}")

    if BUNDLED_RECIPE_PATH.exists():
        # Use bundled recipes (deployment mode)
        RECIPE_PATH = BUNDLED_RECIPE_PATH
        RECIPE_ROOT = RECIPE_PATH.parent
        logger.info(f"Using bundled recipes: {RECIPE_PATH}")
    else:
        # Fall back to repo structure (development mode)
        REPO_ROOT = Path(__file__).resolve().parents[4]
        RECIPE_PATH = REPO_ROOT / "recipes" / "document_generator" / "document_generator_recipe.json"
        RECIPE_ROOT = RECIPE_PATH.parent
        logger.info(f"Using repo recipes: {RECIPE_PATH}")
        logger.info(f"Recipe exists: {RECIPE_PATH.exists()}")

    # Use session-scoped temp directory
    session_dir = session_manager.get_session_dir(session_id)
    tmpdir = str(session_dir / "execution")
    Path(tmpdir).mkdir(exist_ok=True)
    logger.info(f"Using temp directory: {tmpdir}")

    try:
        # Resolve all resources using the new resolver
        logger.info("Resolving resources...")
        outline_data = outline.to_dict()
        logger.info(f"Outline data: {json.dumps(outline_data, indent=2)}")

        resolved_resources = resolve_all_resources(outline_data, session_id)
        logger.info(f"Resolved resources: {resolved_resources}")

        # Update resource paths in outline with resolved paths, converting docx to text if needed
        for resource in outline.resources:
            if resource.key in resolved_resources:
                old_path = resource.path
                resolved_path = str(resolved_resources[resource.key])

                # Always update the path to the resolved path (keeps original file reference)
                resource.path = resolved_path

                # If it's a docx file, convert it to text and save as .txt file
                if resolved_path.lower().endswith(".docx"):
                    try:
                        from ..app import docx_to_text

                        text_content = docx_to_text(resolved_path)

                        # Create a text file version
                        txt_path = resolved_path.replace(".docx", ".txt")
                        with open(txt_path, "w", encoding="utf-8") as f:
                            f.write(text_content)

                        # Set txt_path for recipe executor to use
                        resource.txt_path = txt_path
                        logger.info(
                            f"Converted docx to text: {resource.key}: {old_path} -> {resolved_path}, txt_path: {txt_path}"
                        )
                    except Exception as e:
                        filename = os.path.basename(resolved_path)
                        logger.error(f"Error converting docx file {filename}: {e}")
                        # Re-raise with user-friendly message if it's a protection issue
                        if "protected or encrypted" in str(e):
                            raise e  # Error already includes filename from docx_to_text
                        # Keep txt_path as None on other errors
                else:
                    logger.info(f"Updated resource {resource.key}: {old_path} -> {resource.path}")

        # Create updated outline for recipe execution (use txt_path when available)
        execution_outline = Outline(
            title=outline.title,
            general_instruction=outline.general_instruction,
            resources=[
                Resource(
                    key=res.key,
                    path=res.txt_path if res.txt_path else res.path,  # Use txt_path for recipe execution
                    title=res.title,
                    description=res.description,
                    merge_mode=res.merge_mode,
                    txt_path=res.txt_path,
                )
                for res in outline.resources
            ],
            sections=outline.sections,
        )

        data = execution_outline.to_dict()
        outline_json = json.dumps(data, indent=2)
        outline_path = Path(tmpdir) / "outline.json"
        outline_path.write_text(outline_json)
        logger.info(f"Created outline file for recipe execution: {outline_path}")

        recipe_logger = init_logger(log_dir=tmpdir)

        # Load configuration from environment variables
        config = load_configuration()

        context = Context(
            artifacts={
                "outline_file": str(outline_path),
                "recipe_root": str(RECIPE_ROOT),
                "output_root": str(session_dir),  # Use session directory for output
                "model": settings.model_id,  # Use configured model
            },
            config=config,  # Pass configuration to context
        )
        logger.info(f"Context artifacts: {context.dict()}")

        executor = Executor(recipe_logger)
        logger.info(f"Executing recipe: {RECIPE_PATH}")
        await executor.execute(str(RECIPE_PATH), context)
        logger.info("Recipe execution completed")

        output_root = Path(context.get("output_root", tmpdir))
        filename = context.get("document_filename")
        logger.info(f"Output root: {output_root}")
        logger.info(f"Document filename: {filename}")
        logger.info(f"All context keys: {list(context.keys())}")

        if not filename:
            document_content = context.get("document", "")
            logger.info(f"No filename, returning document from context (length: {len(document_content)})")
            return document_content

        document_path = output_root / f"{filename}.md"
        logger.info(f"Looking for document at: {document_path}")

        try:
            content = document_path.read_text()
            logger.info(f"Successfully read document (length: {len(content)})")
            return content
        except FileNotFoundError:
            logger.error(f"Generated file not found: {document_path}")
            # List files in output directory for debugging
            if output_root.exists():
                files = list(output_root.glob("*"))
                logger.info(f"Files in output directory: {files}")
            return f"Generated file not found: {document_path}"
    except Exception as e:
        logger.error(f"Error generating document: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return f"Error generating document: {str(e)}\n\nFull traceback:\n{traceback.format_exc()}"


async def generate_docpack_from_prompt(
    prompt: str, resources: List[Dict[str, str]], session_id: Optional[str] = None, dev_mode: bool = False
) -> Tuple[str, str]:
    """
    Generate a docpack outline from user prompt and uploaded resources.

    Args:
        prompt: User's description of the document they want to create
        resources: List of uploaded resource files with 'path' and 'name' keys
        session_id: Optional session ID for file management
        dev_mode: Whether running in development mode

    Returns:
        Tuple of (docpack_path, outline_json) where:
        - docpack_path: Path to the generated .docpack file
        - outline_json: JSON string of the generated outline
    """
    logger.info(f"Starting docpack generation for session: {session_id}")
    logger.info(f"Running in {'development' if dev_mode else 'production'} mode")
    logger.info(f"Prompt: {prompt}")
    logger.info(f"Resources: {len(resources)} files")

    # Setup paths
    APP_ROOT = Path(__file__).resolve().parents[2]
    BUNDLED_RECIPE_PATH = APP_ROOT / "document_generator_app" / "recipes" / "generate_docpack.json"

    logger.info(f"APP_ROOT: {APP_ROOT}")
    logger.info(f"BUNDLED_RECIPE_PATH: {BUNDLED_RECIPE_PATH}")
    logger.info(f"Bundled recipe exists: {BUNDLED_RECIPE_PATH.exists()}")

    if BUNDLED_RECIPE_PATH.exists():
        RECIPE_PATH = BUNDLED_RECIPE_PATH
        RECIPE_ROOT = RECIPE_PATH.parent
        logger.info(f"Using bundled recipes: {RECIPE_PATH}")
    else:
        # Fall back to repo structure
        REPO_ROOT = Path(__file__).resolve().parents[4]
        RECIPE_PATH = REPO_ROOT / "recipes" / "document_generator" / "generate_docpack.json"
        RECIPE_ROOT = RECIPE_PATH.parent
        logger.info(f"Using repo recipes: {RECIPE_PATH}")

    # Use session-scoped temp directory
    session_dir = session_manager.get_session_dir(session_id)
    tmpdir = str(session_dir / "docpack_generation")
    Path(tmpdir).mkdir(exist_ok=True)
    logger.info(f"Using temp directory: {tmpdir}")

    try:
        # Extract resource paths and convert docx to text if needed
        # Keep track of original paths and their converted versions
        resource_paths = []
        docx_conversion_map = {}  # Maps txt_path -> original_docx_path

        for resource in resources:
            if "path" in resource and resource["path"]:
                resource_path = resource["path"]

                # If it's a docx file, convert it to text and save as .txt file
                if resource_path.lower().endswith(".docx"):
                    try:
                        from ..app import docx_to_text

                        text_content = docx_to_text(resource_path)

                        # Create a text file version
                        txt_path = resource_path.replace(".docx", ".txt")
                        with open(txt_path, "w", encoding="utf-8") as f:
                            f.write(text_content)

                        resource_paths.append(txt_path)
                        docx_conversion_map[txt_path] = resource_path  # Remember the original path
                        logger.info(f"Converted docx to text: {resource_path} -> {txt_path}")
                    except Exception as e:
                        logger.error(f"Error converting docx file {resource_path}: {e}")
                        # Re-raise with user-friendly message if it's a protection issue
                        if "protected or encrypted" in str(e):
                            raise e
                        resource_paths.append(resource_path)  # Fall back to original path for other errors
                else:
                    resource_paths.append(resource_path)

        logger.info(f"Resource paths: {resource_paths}")

        # Initialize recipe logger
        recipe_logger = init_logger(log_dir=tmpdir)

        # Load configuration
        config = load_configuration()

        # Create timestamp-based docpack name
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        docpack_name = f"{timestamp}.docpack"

        # Create context for the recipe
        context = Context(
            artifacts={
                "model": settings.model_id,
                "output_root": str(session_dir),
                "document_description": prompt,
                "resources": resource_paths,
                "docpack_name": docpack_name,
                "recipe_root": str(RECIPE_ROOT),
            },
            config=config,
        )
        logger.info(f"Context artifacts: {context.dict()}")

        # Execute the generate_docpack recipe
        executor = Executor(recipe_logger)
        logger.info(f"Executing recipe: {RECIPE_PATH}")
        await executor.execute(str(RECIPE_PATH), context)
        logger.info("Recipe execution completed")

        # Get the generated files
        output_root = Path(context.get("output_root", tmpdir))
        docpack_path = output_root / docpack_name
        outline_path = output_root / "outline.json"

        # Read the generated outline and fix docx paths
        outline_json = ""
        if outline_path.exists():
            outline_json = outline_path.read_text()
            logger.info(f"Generated outline loaded from: {outline_path}")

            # If we have docx conversions, fix the paths in the outline
            if docx_conversion_map:
                try:
                    import json

                    outline_data = json.loads(outline_json)

                    # Fix resource paths to point back to original docx files
                    for resource in outline_data.get("resources", []):
                        resource_path = resource.get("path", "")
                        if resource_path in docx_conversion_map:
                            original_path = docx_conversion_map[resource_path]
                            logger.info(f"Restoring original path: {resource_path} -> {original_path}")
                            resource["path"] = original_path  # Restore original docx path
                            resource["txt_path"] = resource_path  # Keep txt path for future use

                    # Save the fixed outline
                    outline_json = json.dumps(outline_data, indent=2)
                    logger.info("Fixed outline paths to preserve original docx references")

                except Exception as e:
                    logger.error(f"Error fixing outline paths: {e}")
                    # Continue with original outline_json if fixing fails

        else:
            logger.error(f"Outline file not found at: {outline_path}")

        # Check if docpack was created
        if not docpack_path.exists():
            logger.error(f"Docpack file not found at: {docpack_path}")
            # List files for debugging
            if output_root.exists():
                files = list(output_root.glob("*"))
                logger.info(f"Files in output directory: {files}")
            return "", outline_json

        logger.info(f"Successfully generated docpack at: {docpack_path}")
        return str(docpack_path), outline_json

    except Exception as e:
        logger.error(f"Error generating docpack: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise


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
from jsonschema import validate


@dataclass
class Resource:
    key: str
    path: str
    title: str
    description: str
    merge_mode: str
    txt_path: Optional[str] = None  # Path to converted text file (for docx files)


@dataclass
class Section:
    title: str
    prompt: Optional[str] = None
    refs: List[str] = field(default_factory=list)
    resource_key: Optional[str] = None
    sections: List["Section"] = field(default_factory=list)
    _mode: Optional[str] = field(default=None, init=False, repr=False)  # Internal mode tracking

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict, excluding None values and empty refs to match schema."""
        result: Dict[str, Any] = {"title": self.title}

        # Use mode to determine which fields to include
        if self._mode == "Static" and self.resource_key is not None:
            result["resource_key"] = self.resource_key
        else:
            # Default to prompt mode
            if self.prompt is not None:
                result["prompt"] = self.prompt
            if self.refs:  # Only include refs if not empty
                result["refs"] = self.refs

        # Always include sections array (even if empty)
        result["sections"] = [s.to_dict() for s in self.sections]

        return result


def section_from_dict(data: Dict[str, Any]) -> Section:
    section = Section(
        title=data.get("title", ""),
        prompt=data.get("prompt"),
        refs=list(data.get("refs", [])),
        resource_key=data.get("resource_key"),
        sections=[section_from_dict(s) for s in data.get("sections", [])],
    )
    # Set mode based on loaded data
    if section.resource_key is not None:
        section._mode = "Static"
    else:
        section._mode = "Prompt"
    return section


@dataclass
class Outline:
    title: str
    general_instruction: str
    resources: List[Resource] = field(default_factory=list)
    sections: List[Section] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert outline to dict with proper section serialization."""
        return {
            "title": self.title,
            "general_instruction": self.general_instruction,
            "resources": [asdict(r) for r in self.resources],
            "sections": [s.to_dict() for s in self.sections],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Outline":
        res_list: List[Resource] = []
        for r in data.get("resources", []):
            res_list.append(
                Resource(
                    key=r.get("key", ""),
                    path=r.get("path", ""),
                    title=r.get("title", ""),
                    description=r.get("description", ""),
                    merge_mode=r.get("merge_mode", "concat"),
                    txt_path=r.get("txt_path"),
                )
            )
        sec_list: List[Section] = [section_from_dict(s) for s in data.get("sections", [])]
        return cls(
            title=data.get("title", ""),
            general_instruction=data.get("general_instruction", ""),
            resources=res_list,
            sections=sec_list,
        )


# JSON Schema for outline validation
OUTLINE_SCHEMA = {
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
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "merge_mode": {"type": "string", "enum": ["concat", "dict"]},
                    "txt_path": {"type": "string"},
                },
                "required": ["key", "path", "title", "description"],
                "additionalProperties": False,
            },
        },
        "sections": {"type": "array", "items": {"$ref": "#/definitions/section"}},
    },
    "definitions": {
        "section": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "prompt": {"type": "string"},
                "refs": {"type": "array", "items": {"type": "string"}},
                "resource_key": {"type": "string"},
                "sections": {"type": "array", "items": {"$ref": "#/definitions/section"}},
            },
            "required": ["title"],
            "oneOf": [{"required": ["prompt"]}, {"required": ["resource_key"]}],
            "additionalProperties": False,
        }
    },
    "required": ["title", "general_instruction", "resources", "sections"],
    "additionalProperties": False,
}


def validate_outline(data: dict) -> None:
    """
    Validate outline data against the JSON schema.
    Raises jsonschema.ValidationError on failure.
    """
    validate(instance=data, schema=OUTLINE_SCHEMA)


=== File: apps/document-generator/document_generator_app/resource_resolver.py ===
"""Resource resolution for document generation.

Handles resolving resources at generation time:
- Uploaded files: resolved to session files directory
- URLs: downloaded to session temp directory
"""

import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from .models.outline import Resource
from .session import session_manager


def resolve_resource(resource: Resource, session_id: Optional[str]) -> Path:
    """Resolve a resource to a local file path for generation.

    Args:
        resource: Resource object with path (file or URL)
        session_id: Session ID for directory resolution

    Returns:
        Path to local file for use in generation

    Raises:
        FileNotFoundError: If uploaded file doesn't exist
        urllib.error.URLError: If URL download fails
    """
    if resource.path.startswith(("http://", "https://")):
        # URL: download to temp directory
        return _download_url_resource(resource, session_id)
    else:
        # Uploaded file: resolve to files directory
        return _resolve_file_resource(resource, session_id)


def _resolve_file_resource(resource: Resource, session_id: Optional[str]) -> Path:
    """Resolve uploaded file resource to local path."""
    files_dir = session_manager.get_files_dir(session_id)
    file_path = files_dir / resource.path

    if not file_path.exists():
        raise FileNotFoundError(f"Resource file not found: {resource.path}")

    return file_path


def _download_url_resource(resource: Resource, session_id: Optional[str]) -> Path:
    """Download URL resource to temp directory."""
    temp_dir = session_manager.get_temp_dir(session_id)

    # Generate filename from URL
    parsed_url = urlparse(resource.path)
    filename = Path(parsed_url.path).name

    # If no filename in URL, use resource key
    if not filename or filename == "/":
        filename = f"{resource.key}.downloaded"

    target_path = temp_dir / filename

    # Download the file
    try:
        urllib.request.urlretrieve(resource.path, target_path)
        return target_path
    except Exception as e:
        raise urllib.error.URLError(f"Failed to download {resource.path}: {str(e)}")


def resolve_all_resources(outline_data: Dict[str, Any], session_id: Optional[str]) -> Dict[str, Path]:
    """Resolve all resources in an outline to local paths.

    Args:
        outline_data: Outline dictionary with resources
        session_id: Session ID for directory resolution

    Returns:
        Dictionary mapping resource keys to resolved file paths
    """
    from .models.outline import Outline

    outline = Outline.from_dict(outline_data)
    resolved_resources = {}

    for resource in outline.resources:
        if resource.key:
            resolved_resources[resource.key] = resolve_resource(resource, session_id)

    return resolved_resources


=== File: apps/document-generator/document_generator_app/session.py ===
"""
Session management for multi-user hosting.

Provides session-scoped temporary directories to isolate user data.
"""

import uuid
import tempfile
from pathlib import Path
import shutil
import atexit
from typing import Optional


class SessionManager:
    """Dead simple session directory management"""

    def __init__(self):
        self.session_dirs = {}
        atexit.register(self.cleanup_all)

    def get_session_dir(self, session_id: Optional[str] = None) -> Path:
        """Get unique temp directory for session"""
        if not session_id:
            session_id = str(uuid.uuid4())

        if session_id not in self.session_dirs:
            session_dir = Path(tempfile.gettempdir()) / f"doc-gen-{session_id}"
            session_dir.mkdir(exist_ok=True)

            # Create subdirectories for organized file management
            (session_dir / "files").mkdir(exist_ok=True)  # Uploaded files (stored in docpack)
            (session_dir / "temp").mkdir(exist_ok=True)  # Generated files, downloaded URLs

            self.session_dirs[session_id] = session_dir

        return self.session_dirs[session_id]

    def get_files_dir(self, session_id: Optional[str] = None) -> Path:
        """Get files directory for session (for uploaded files)"""
        return self.get_session_dir(session_id) / "files"

    def get_temp_dir(self, session_id: Optional[str] = None) -> Path:
        """Get temp directory for session (for generated files and downloaded URLs)"""
        return self.get_session_dir(session_id) / "temp"

    def cleanup_all(self):
        """Clean up all session directories on shutdown"""
        for session_dir in self.session_dirs.values():
            shutil.rmtree(session_dir, ignore_errors=True)


# Global instance
session_manager = SessionManager()


=== File: apps/document-generator/document_generator_app/static/css/styles.css ===
/* Document Builder Custom Styles */

/* Color Palette */
:root {
    --primary-teal: #4a9d9e;
    --primary-teal-dark: #2d7474;
    --primary-teal-light: #e8f5f5;
    --secondary-tangerine: #ff9966;
    --secondary-tangerine-dark: #d47239;
    --secondary-tangerine-light: #fff7f0;
    --gradient-primary: linear-gradient(135deg, #4a9d9e 0%, #ff9966 100%);
    --gradient-reverse: linear-gradient(135deg, #ff9966 0%, #4a9d9e 100%);
    --gradient-subtle: linear-gradient(135deg, #f0f9f9 0%, #fff7f0 100%);
}

/* Ensure tab content is visible when active */
.gradio-container .tab-nav + div > div[id^="component-"]:not([style*="display: none"]) {
    visibility: visible !important;
    opacity: 1 !important;
}

/* Remove all focus outlines from specific inputs */
.doc-title-box input,
.doc-title-box textarea,
.doc-description-box input,
.doc-description-box textarea,
.start-prompt-input input,
.start-prompt-input textarea {
    outline: none !important;
    outline-width: 0 !important;
    outline-style: none !important;
}

.doc-title-box input:focus,
.doc-title-box textarea:focus,
.doc-description-box input:focus,
.doc-description-box textarea:focus,
.start-prompt-input input:focus,
.start-prompt-input textarea:focus {
    outline: none !important;
    outline-width: 0 !important;
    outline-style: none !important;
    box-shadow: none !important;
    -webkit-box-shadow: none !important;
}

/* Override Gradio's focus styles */
.doc-title-box .wrap:has(textarea:focus),
.doc-description-box .wrap:has(textarea:focus),
.start-prompt-input .wrap:has(textarea:focus) {
    border-color: transparent !important;
    box-shadow: none !important;
    outline: none !important;
}

/* Start Tab Styles */
.start-tab-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 20px;
}

/* Welcome message styles */
.start-welcome-title {
    text-align: center;
    padding-top: 20px;
}

.start-welcome-title h1 {
    font-size: 72px !important;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0;
    letter-spacing: -1px;
}

.start-welcome-subtitle {
    text-align: center;
    color: #666;
    font-weight: 400;
    letter-spacing: 0.5px;
}

.start-welcome-subtitle .prose {
    font-size: 16px;
}
/* Get Started button */
.start-get-started-btn {
    background: #4a9d9e !important;
    border: 1px solid #4a9d9e !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 8px 16px !important;
    border-radius: 6px !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
    width: 100% !important;
    height: auto !important;
}

/* Draft button specific styling */
.start-draft-btn {
    margin-top: 20px !important;
    margin-left: 12px !important;
    margin-right: 12px !important;
    width: calc(100% - 24px) !important;
}

.start-get-started-btn:hover {
    background: #3a8d8e !important;
    border-color: #3a8d8e !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(74, 157, 158, 0.3) !important;
}

/* Spacer for future content */
.start-content-spacer {
    min-height: 20px;
}

/* Introduction section */
.start-intro-section {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid #e5e5e5;
}

.start-intro-content {
    font-size: 16px;
    line-height: 1.8;
    color: #444;
}

.start-intro-content h3 {
    font-size: 20px;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 20px;
    margin-top: 0;
}

.start-intro-content ul {
    margin-left: 20px;
    list-style-type: disc;
    padding-left: 20px;
}

.start-intro-content ul li {
    margin-bottom: 8px;
    list-style-type: disc;
}

.start-intro-content p {
    margin-top: 24px;
    color: #555;
}

/* Hide components but keep them in DOM */
.hidden-component {
    display: none !important;
}

/* Hide the parent div.form container when it contains a hidden-component */
.form:has(.hidden-component) {
    display: none !important;
}

/* Start tab input card container */
.start-input-card-container {
    max-width: 800px;
    margin: 30px auto 90px;
}

/* Start tab input card - single expanding card */
.start-input-card {
    background: white;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid #e5e5e5;
    transition: all 0.4s ease;
    gap: 0px;
}

.start-input-card .form {
    border: 1px solid white;
}

.start-input-card.has-expanded {
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

/* Example buttons styling */
.start-examples-container {
    padding: 0 12px 0 12px;
    width: 100%;
}

.start-examples-buttons {
    gap: 12px;
    display: flex !important;
    flex-wrap: wrap;
}

.start-example-btn {
    background: #e8f5f5 !important;
    border: 1px solid #b8dfe0 !important;
    padding: 4px 12px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    min-height: 32px !important;
    height: 32px !important;
    box-shadow: 0 1px 3px rgba(74, 157, 158, 0.15);
}

.start-example-btn:hover {
    background: #b8dfe0 !important;
    border-color: #4a9d9e !important;
    transform: translateY(-1px);
    box-shadow: 0 3px 8px rgba(74, 157, 158, 0.2);
}

/* Start tab bottom row */
.start-bottom-row {
    gap: 20px;
    align-items: stretch;
}

/* Expandable content - initially hidden */
.start-expandable-content {
    gap: 0px;
    max-height: 0;
    opacity: 0;
    overflow: hidden;
    transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease;
}

.start-expandable-content.expanded {
    max-height: 500px; /* Adjust based on your content */
    opacity: 1;
    transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease;
}

/* Resources display container */
.start-resources-display-container {
    min-height: 0;
}

/* Resources list */
.start-resources-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: flex-start;
    min-height: 0;
    margin-bottom: 12px;
}

/* Override any Gradio row styling for resources */
.start-resources-list.row {
    flex-direction: row !important;
}

.start-resources-list .wrap {
    flex-wrap: wrap !important;
    gap: 8px !important;
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Adjust input card when expanded */
.start-input-card:has(+ .start-expandable-content.expanded) {
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
    margin-bottom: 0;
}

/* Start tab upload area - left side */
.start-upload-area {
    padding: 0;
    background: transparent;
    gap: 0;
}

/* Start tab button column - right side */
.start-button-column {
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Start tab feature card */
.start-feature-card {
    width: 100vw;
    margin-left: calc(-50vw + 50%);
    margin-right: calc(-50vw + 50%);
    margin-bottom: 40px;
    background: #e4e4e7;
    padding: 60px 20px;
}

/* Inner container to maintain max-width for content */
.start-feature-card > * {
    max-width: 1000px;
    margin-left: auto;
    margin-right: auto;
}

.start-feature-title {
    text-align: center;
    margin-bottom: 8px;
}

.start-feature-title h3 {
    font-size: 32px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0;
}

.start-feature-description {
    text-align: center;
    color: #666;
    font-size: 16px;
    line-height: 1.6;
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
}

/* Features grid */
.start-features-grid {
    gap: 24px;
    margin-top: 32px;
    display: flex !important;
    flex-direction: row !important;
    align-items: stretch !important;
}

.start-features-grid > div {
    flex: 1 1 0 !important;
    min-width: 0 !important;
}

.start-feature-item {
    text-align: center;
    padding: 28px 24px;
    background: white;
    border-radius: 8px;
    border: 1px solid #e5e5e5;
    transition: all 0.2s ease;
}

.start-feature-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    border-color: #4a9d9e;
}

/* Ensure feature images and text don't show pointer/text cursor */
.start-feature-image,
.start-feature-image img,
.start-feature-image button,
.start-feature-item-title,
.start-feature-item-title *,
.start-feature-item-text,
.start-feature-item-text * {
    cursor: default !important;
}

.start-feature-item-title h3 {
    font-size: 18px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 8px 0;
}

.start-feature-use-case {
    background: #e8f5f5;
    border-radius: 6px;
    padding: 6px 12px;
    margin-bottom: 12px;
    font-size: 13px;
    color: #555;
    display: inline-block;
}

.start-feature-use-case strong {
    font-weight: 600;
    color: #2d7474;
}

.start-feature-item-text {
    font-size: 14px;
    line-height: 1.6;
    color: #666;
}

/* Benefits section */
.start-benefits-section {
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px solid #e9ecef;
}

.start-benefits-text {
    font-size: 15px;
    line-height: 1.7;
    color: #555;
    background: #f8f9fa;
    padding: 20px 24px;
    border-radius: 8px;
    border-left: 4px solid #4a9d9e;
}

.start-benefits-text strong {
    color: #1a1a1a;
    font-weight: 600;
}

/* Process section */
.start-process-section {
    max-width: 1000px;
    margin: 40px auto;
    background: white;
    padding: 40px;
    border-radius: 8px;
    border: 1px solid #e5e5e5;
}

.start-process-title {
    text-align: center;
    margin-bottom: 8px;
}

.start-process-title h2 {
    font-size: 32px;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0;
}

.start-process-subtitle {
    text-align: center;
    font-size: 16px;
    color: #666;
}

/* Process container */
.start-process-container {
    gap: 40px;
    margin-top: 32px;
    align-items: stretch;
}

/* Vertical steps layout */
.start-process-steps-vertical {
    display: flex;
    flex-direction: column;
    gap: 0;
}

.start-process-step-vertical {
    padding: 24px;
    margin-bottom: 16px;
    background: white;
    border-radius: 8px;
    border: 1px solid #e5e5e5;
    transition: all 0.2s ease;
    cursor: default;
    opacity: 0.7;
}

.start-process-step-vertical:hover,
.start-process-step-vertical.active {
    opacity: 1;
    border-color: #4a9d9e;
    box-shadow: 0 4px 12px rgba(74, 157, 158, 0.15);
    background: #fafffe;
}

.start-step-number-col {
    display: flex;
    align-items: center;
    justify-content: center;
}

.start-step-number-vertical {
    width: 40px;
    height: 40px;
    background: #e8f5f5;
    color: #4a9d9e;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 700;
    transition: all 0.3s ease;
}

.start-process-step-vertical:hover .start-step-number-vertical,
.start-process-step-vertical.active .start-step-number-vertical {
    background: #ff9966;
    color: white;
    box-shadow: 0 4px 12px rgba(255, 153, 102, 0.3);
    transform: scale(1.05);
}

.start-step-content {
    padding-left: 16px;
}

.start-step-title h3 {
    font-size: 18px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 8px 0;
}

.start-step-description {
    font-size: 14px;
    line-height: 1.6;
    color: #666;
}

/* Process visual */
.start-process-visual {
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
    border-radius: 8px;
    border: 1px solid #e5e5e5;
    padding: 32px;
    min-height: 400px;
}

.process-visual-placeholder {
    text-align: center;
    width: 100%;
    max-width: 400px;
}

.visual-content svg {
    width: 100%;
    height: auto;
    max-width: 300px;
    margin: 0 auto;
}

.visual-caption {
    margin-top: 20px;
    font-size: 14px;
    color: #666;
    font-style: italic;
}

/* Section header */
.start-section-header {
    max-width: 800px;
    margin: 30px auto 40px;
    text-align: center;
}

.start-section-title h2 {
    font-size: 32px;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 8px 0;
}

.start-section-subtitle {
    font-size: 16px;
    color: #666;
    margin: 0;
}

.start-prompt-input {
    width: 100%;
    border: 0px;
}

.start-prompt-input textarea {
    font-size: 15px;
    line-height: 1.6;
    color: #333;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 12px;
    min-height: 120px !important;  /* Ensure minimum height for 4 lines */
    resize: vertical;
}

.start-prompt-input textarea:focus {
    border-color: #ddd !important;
    outline: none !important;
    box-shadow: none !important;
}

/* Start tab resources title */
.start-resources-title {
    font-size: 16px;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 15px;
    margin-top: 0;
}

.start-resources-title h3 {
    margin: 0 0 8px 0;
    font-size: 18px;
    font-weight: 600;
}

.start-resources-subtitle {
    font-size: 14px;
    color: #666;
    margin-bottom: 16px;
}

/* Start tab file upload dropzone - matching tab 2 style */
.start-file-upload-dropzone {
    width: calc(100% - 24px) !important;
    min-height: 90px !important;
    max-height: 90px !important;
    border: 1px dashed #4a9d9e !important;
    border-radius: 8px !important;
    background-color: #f8fafa !important;
    transition: all 0.3s ease !important;
    margin: 0 12px 12px 12px !important;
}

.start-file-upload-dropzone:hover {
    border-color: #3a8d8e !important;
    background-color: #f0f9f9 !important;
}

.start-file-upload-dropzone.dragging,
.start-file-upload-dropzone.drag-over {
    border-color: #4a9d9e !important;
    background-color: #e8f5f5 !important;
    border-width: 1px !important;
}

.start-file-upload-dropzone > div {
    height: 56px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.start-file-upload-dropzone label {
    font-size: 11px !important;
    color: #666 !important;
}

.start-file-upload-dropzone .wrap {
    font-size: 12px !important;
    padding-top: 5px;
}

.start-file-upload-dropzone .wrap .or {
    font-size: 11px !important;
    margin: 0 3px !important;
}

.start-file-upload-dropzone .feather-upload {
    width: 90%;
    height: 90%;
}

.start-file-upload-dropzone .icon-wrap {
    width: 24px;
    height: 18px;
    margin-bottom: 0;
}

.start-file-upload-dropzone .file-preview {
    display: none !important;
}

.start-file-upload-dropzone input[type="file"] {
    opacity: 0 !important;
    position: absolute !important;
    width: 100% !important;
    height: 100% !important;
    cursor: pointer !important;
}

/* Start tab resources display */
.resource-drop-label {
    padding-top: 12px;
    padding-bottom: 0px;
}
.resource-drop-label .input-container *{
    height: 0px;
}

/* Hide the textbox but keep the label */
.resource-drop-label textarea,
.resource-drop-label input[type="text"] {
    display: none !important;
}

/* Also hide the container wrapper if it has padding/margin */
.resource-drop-label .wrap,
.resource-drop-label .input-container {
    min-height: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}

.start-resources-display{
    margin-top: 0px;
    gap: 8px;
}

.start-resources-display .html-container{
    padding-top: 0px;
}
.start-resource-item {
    background: #f8f9fa;
    border: 1px solid #e5e5e5;
    border-radius: 6px;
    padding: 12px;
    transition: all 0.2s ease;
}

.start-resource-item:hover {
    border-color: #d0d0d0;
    background: #f5f6f7;
}

.start-resource-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex: 1;
}

.start-resource-name {
    font-size: 14px;
    color: #333;
    font-weight: 500;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.start-resource-size {
    font-size: 12px;
    color: #666;
    margin-left: 10px;
    white-space: nowrap;
}

.start-resource-remove-btn {
    padding: 4px 12px !important;
    font-size: 12px !important;
    border-radius: 4px !important;
    background: white !important;
    border: 1px solid #ddd !important;
    color: #666 !important;
}

.start-resource-remove-btn:hover {
    background: #f8f9fa !important;
    border-color: #999 !important;
    color: #333 !important;
}


/* Debug Panel Accordion Styles */
.debug-panel {
    border: 1px solid #ddd;
    border-radius: 8px;
    background: white;
    margin-top: 10px;
}

/* Hide debug panel content initially */
.debug-panel-content {
    display: none;
}

.debug-panel-header {
    padding: 0;
    margin: 0;
}

.debug-panel-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    cursor: pointer;
    user-select: none;
    font-weight: 600;
    font-size: 14px;
    color: #333;
    background: #f8f9fa;
    border-radius: 8px 8px 0 0;
    transition: background-color 0.2s;
}

.debug-panel-title:hover {
    background: #e9ecef;
}

.debug-collapse-icon {
    margin-left: 8px;
    font-size: 16px;
    color: #666;
    transition: color 0.2s;
}

.debug-panel-title:hover .debug-collapse-icon {
    color: #333;
}

.debug-panel-content {
    border-top: 1px solid #ddd;
    padding: 0 !important;
}

.debug-panel-content > div {
    margin: 0 !important;
}

.json-debug-output {
    border-radius: 0 0 8px 8px !important;
    margin: 0 !important;
}

/* Main gradio container */
.gradio-container {
    background-color: #f5f5f5 !important;
    padding-left: 10px !important;
    padding-right: 10px !important;
}
.gradio-container .fillable {
    margin-left: 0 !important;
    margin-right: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
}

.doc-title-box, .doc-description-box {
    background: white !important;
}

.app-header-col {
    gap: 7px !important;
    max-width: 450px;
}


/* Builder buttons */
.save-builder-btn {
    width: 120px !important;
    min-width: 120px !important;
    max-width: 120px !important;
    height: 30px !important;
}
.import-builder-btn {
    width: 120px !important;
    min-width: 120px !important;
    max-width: 120px !important;
    height: 30px !important;
}
.new-builder-btn {
    width: 120px !important;
    min-width: 120px !important;
    max-width: 120px !important;
    height: 30px !important;
    background-color: #ffffff !important;
    border: 1px solid #d0d0d0 !important;
    color: #333333 !important;
}
.new-builder-btn:hover {
    background-color: #f5f5f5 !important;
    border-color: #b0b0b0 !important;
}

/* Header buttons row - base styling */
.header-buttons-row {
    display: flex !important;
    flex-wrap: wrap !important;
    justify-content: flex-end !important;
    gap: 8px !important;
    align-items: center !important;
}

/* Ensure all direct children of header-buttons-row are vertically aligned */
.header-buttons-row > * {
    align-self: center !important;
    vertical-align: middle !important;
}

/* At larger screens, Template Examples button should align right in its container */
.try-examples-container .try-examples-btn {
    margin-left: auto !important;
    display: block !important;
}

/* Button spacer should shrink when buttons wrap */
.button-spacer {
    flex: 1 1 auto !important;
    min-width: 0 !important;
}

/* Responsive button container adjustments */
@media (max-width: 1280px) {
    /* Hide spacer at smaller screens to allow proper wrapping */
    .button-spacer {
        display: none !important;
    }
    
    /* Ensure button row maintains right alignment when wrapping */
    .header-buttons-row {
        justify-content: flex-end !important;
    }
    
    /* When buttons wrap, we need each row to align right
       Target all children except the hidden spacer */
    .header-buttons-row > *:not(.button-spacer) {
        flex: 0 0 auto !important;
    }
}

@media (max-width: 1024px) {
    /* Continue hiding spacer */
    .button-spacer {
        display: none !important;
    }
    
    /* Maintain right alignment for wrapped buttons */
    .header-buttons-row {
        justify-content: flex-end !important;
    }
}

@media (max-width: 900px) {
    /* Hide spacer */
    .button-spacer {
        display: none !important;
    }
    
    /* Stack buttons vertically, all right-aligned */
    .header-buttons-row {
        flex-direction: column !important;
        align-items: flex-end !important;
        gap: 8px !important;
    }
    
    /* Reset container styles to prevent centering */
    .try-examples-container {
        width: auto !important;
        display: block !important;
        margin: 0 !important;
    }
    
    /* Keep Template Examples button right-aligned within its container */
    .try-examples-container .try-examples-btn {
        margin-left: auto !important;
        margin-right: 0 !important;
        display: block !important;
    }
    
    /* Reset all button margins for clean vertical stack */
    .new-builder-btn,
    .import-builder-btn,
    .save-builder-btn {
        margin-left: 0 !important;
        margin-right: 0 !important;
        width: 120px !important;
    }
    
    /* Ensure all direct children align to the end */
    .header-buttons-row > * {
        align-self: flex-end !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }
}

/* Try Examples button - citrus orange tertiary color */
.try-examples-btn {
    position: relative !important;
    width: 120px !important;
    min-width: 120px !important;
    max-width: 120px !important;
    height: 30px !important;
    background-color: #ff9f40 !important;
    border: 1px solid #ff9f40 !important;
    color: white !important;
}
.try-examples-btn:hover {
    background-color: #ff8f20 !important;
    border-color: #ff8f20 !important;
}

/* Try Examples dropdown container */
.try-examples-container {
    position: relative !important;
    display: inline-flex !important;
    justify-content: flex-end !important;
    width: auto !important;
    padding: 0 !important;
    margin: 0 !important;
    min-height: auto !important;
    height: auto !important;
}

/* Remove default Gradio column padding/margins from try-examples-container */
.try-examples-container.svelte-1gfkn6j,
.try-examples-container > .wrap,
.try-examples-container .form {
    padding: 0 !important;
    margin: 0 !important;
    gap: 0 !important;
    min-height: auto !important;
    background: transparent !important;
    border: none !important;
    display: flex !important;
    justify-content: flex-end !important;
}

/* Examples dropdown styling */
.examples-dropdown {
    position: absolute !important;
    top: 30px !important;
    right: 0 !important;
    margin-top: 4px !important;
    min-width: 250px !important;
    background-color: #ffffff !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 8px !important;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15) !important;
    z-index: 1000 !important;
    display: none !important;
    padding: 8px !important;
    padding-left: 6px !important;
}

/* Show dropdown on hover */
.try-examples-container:hover .examples-dropdown {
    display: block !important;
}

/* Create invisible bridge to maintain hover state */
.examples-dropdown::before {
    content: "";
    position: absolute;
    top: -6px;
    left: 0;
    right: 0;
    height: 6px;
    background: transparent;
}

/* Individual example items */
.examples-dropdown-item {
    padding: 12px 16px;
    cursor: pointer;
    border-radius: 6px;
    transition: all 0.2s ease;
    margin-bottom: 4px;
}

.examples-dropdown-item:last-child {
    margin-bottom: 0;
}

.examples-dropdown-item:hover {
    background-color: #fff5eb;
    transform: translateX(4px);
}

/* Example title */
.example-title {
    font-weight: 600;
    font-size: 14px;
    color: #333;
    margin-bottom: 4px;
}

/* Example description */
.example-desc {
    font-size: 12px;
    color: #666;
    line-height: 1.4;
}

/* Active/selected state */
.examples-dropdown-item:active {
    background-color: #ffe5cc;
}


/* Header section */
.header-section {
    background-color: #ffffff !important;
    border-radius: 8px !important;
}
.header-section .form {
    border: 1px solid #ffffff;
}
.header-section textarea {
    border: 1px solid #e0e0e0 !important;
    background-color: #ffffff !important;
}
.header-section textarea:focus,
.header-section textarea:active,
.header-section textarea:hover {
    border: 1px solid #e0e0e0 !important;
    background-color: #ffffff !important;
    outline: none !important;
    box-shadow: none !important;
}
.doc-title-box textarea {
    font-weight: bold !important;
    font-size: 14px !important;
}
.doc-title-box textarea:focus,
.doc-title-box textarea:active,
.doc-title-box textarea:hover {
    border: 1px solid #e0e0e0 !important;
    background-color: #ffffff !important;
    outline: none !important;
    box-shadow: none !important;
}
.doc-description-box {
    position: relative;
}

.doc-description-box textarea {
    font-size: 13px !important;
    line-height: 1.4 !important;
    resize: none !important; /* Disable manual resize since we auto-expand */
    overflow-y: hidden !important; /* Hide scrollbar */
    max-height: none !important; /* No max height */
    transition: none; /* Remove transition for row-based sizing */
}


.doc-description-box textarea:focus,
.doc-description-box textarea:active,
.doc-description-box textarea:hover {
    border: 1px solid #e0e0e0 !important;
    background-color: #ffffff !important;
    outline: none !important;
    box-shadow: none !important;
}

/* Collapsed textarea state */
.doc-description-box.collapsed textarea {
    overflow: hidden !important;
    cursor: text !important;
}

/* Description expand/collapse button */
.desc-expand-btn {
    position: absolute;
    top: 0px;
    right: 3px;
    width: 14px;
    height: 20px;
    padding: 0;
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 12px;
    line-height: 20px;
    color: #999;
    display: none; /* Hidden by default */
    z-index: 10;
}

.desc-expand-btn:hover {
    color: #666;
}

.desc-expand-btn:focus {
    outline: none;
}

/* Rotate chevron for document description to match content blocks */
.doc-description-box:not(.collapsed) .desc-expand-btn {
    transform: rotate(180deg);
}

.doc-description-box.collapsed .desc-expand-btn {
    transform: rotate(0deg);
    top: -2px;
    /* Add your custom positioning here */
}

/* Remove chevron adjustment - it should stay in fixed position */


/* Download button */
.download-generated-doc {
    margin-top: 10px;
    width: 100%;
}

/* Save status message */
.save-status-message {
    margin-top: 10px;
    padding: 8px;
    border-radius: 4px;
    font-size: 12px;
}

.save-status-message p {
    margin: 0;
    color: #4CAF50;
}

/* Debug Panel */
.debug-panel {
    margin-top: 20px;
    padding: 15px;
    background-color: #f8f8f8;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
}

.debug-panel h3 {
    margin-top: 0;
    margin-bottom: 10px;
    font-size: 14px;
    color: #666;
}

.json-debug-output {
    font-size: 12px;
    max-height: 400px;
}

/* Resources */
.resources-col {
    width: 190px !important;
    min-width: 190px !important;
    max-width: 190px !important;
    margin-right: 5px !important;
    gap: 10px !important;
}

/* Reduce gap between resource items */
.resources-display-area > div {
    gap: 4px !important;
}

/* File upload dropzone styling */
.file-upload-dropzone {
    width: 100% !important;
    min-height: 90px !important;
    max-height: 90px !important;
    border: 1px dashed #4a9d9e !important;
    border-radius: 8px !important;
    background-color: #f8fafa !important;
    transition: all 0.3s ease !important;
}

.file-upload-dropzone:hover {
    border-color: #3a8d8e !important;
    background-color: #f0f9f9 !important;
}

/* When dragging files over - match AI content block drag-over effect */
.file-upload-dropzone.dragging,
.file-upload-dropzone.drag-over {
    border-color: #4a9d9e !important;
    background-color: #e8f5f5 !important;
    border-width: 1px !important;
}

/* Style the file input container */
.file-upload-dropzone > div {
    height: 56px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Style the label text */
.file-upload-dropzone label {
    font-size: 11px !important;
    color: #666 !important;
}

/* Make the upload text smaller */
.file-upload-dropzone .wrap {
    font-size: 12px !important;
    padding-top: 5px;
}

.file-upload-dropzone .wrap .or {
    font-size: 11px !important;
    margin: 0 3px !important;
}

.file-upload-dropzone .feather-upload {
    width: 90%;
    height: 90%;
}
.file-upload-dropzone .icon-wrap {
    width: 24px;
    height: 18px;
    margin-bottom: 0;
}
/* Style the file input button area */
.file-upload-dropzone .file-preview {
    display: none !important;
}

.file-upload-dropzone input[type="file"] {
    opacity: 0 !important;
    position: absolute !important;
    width: 100% !important;
    height: 100% !important;
    cursor: pointer !important;
}

.resources-display-area .html-container {
    padding: 0px !important;
}

.resources-display-area {
    gap: 5px !important;
}

.resource-item,
.resource-item-gradio {
    padding: 6px;
    margin-bottom: 4px;
    background-color: #f5f5f5 !important; /* Light gray background */
    border: 1px solid;
    border-color: #4a9d9e !important; /* Keep teal-green border */
    border-radius: 4px;
    font-size: 11px;
    cursor: grab;
    user-select: none;
    transition: transform 0.2s ease;
    position: relative;
}

.resource-content {
    width: 100%;
}
.resource-item.dragging,
.resource-item-gradio.dragging {
    opacity: 0.5;
    cursor: grabbing;
}

/* Resource header for title and controls */
.resource-header {
    display: flex;
    align-items: center;
    width: 100%;
    gap: 4px;
}

/* Resource title input field */
.resource-title-input {
    flex: 1;
    background: white;
    border: 1px solid #e0e0e0;
    font-size: 11px;
    padding: 2px 4px;
    margin: 0;
    outline: none;
    cursor: text;
    user-select: text;
    font-family: inherit;
    border-radius: 2px;
    font-weight: bold;
}

.resource-title-input:hover {
    border-color: #ccc;
}

.resource-title-input:focus {
    border-color: #e0e0e0; /* Keep same border color as default */
    /* No padding change to prevent size shift */
}

/* Gradio resource title styling */
.resource-info-col.form {
    border: 0;
    background: #f5f5f5 !important;
}

/* Ensure the info column itself has the right background */
.resource-info-col {
    background: #f5f5f5 !important;
}


/* Remove the extra filename alignment rules */

.resource-title-gradio {
    padding: 0;
    padding-right: 26px;
    border: 0;
    background: transparent;
}

.resource-title-gradio.show-textbox-border {
    border: 0;
}

.resource-title-gradio input, .resource-title-gradio textarea {
    background: white !important;
    font-size: 11px !important;
    padding: 2px 4px !important;
    margin: 0 !important;
    outline: none !important;
    cursor: text;
    user-select: text;
    font-family: inherit !important;
    border-radius: 2px !important;
    font-weight: bold !important;
    width: 100% !important;
    min-height: unset !important;
    height: 24px !important;
    display: block !important;
    box-sizing: border-box !important;
    border: 1px solid #e0e0e0 !important;
}

/* Force textarea to behave like single-line input */
.resource-title-gradio textarea {
    overflow: hidden !important;
    resize: none !important;
    white-space: nowrap !important;
    text-overflow: ellipsis !important;
    rows: 1 !important;
    line-height: 20px !important;
    max-height: 24px !important;
}

.resource-title-gradio input:hover, .resource-title-gradio textarea:hover{
    border-color: #ccc !important;
}

.resource-title-gradio input:focus, .resource-title-gradio textarea:focus {
    outline: none !important;
    box-shadow: none !important;
}

.resource-desc-gradio {
    padding: 0;
    border: 0;
    background: transparent;
    position: relative;
}

.resource-desc-gradio textarea {
    width: 100% !important;
    padding: 4px 16px 4px 6px !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 3px !important;
    font-size: 11px !important;
    line-height: 1.4 !important;
    font-family: inherit !important;
    resize: none !important;
    overflow-y: hidden !important;
    background: white !important;
    transition: border-color 0.2s ease !important;
    cursor: text;
    user-select: text;
    margin-top: 4px !important;
    display: block !important;
    box-sizing: border-box !important;
    height: auto !important; /* Let rows attribute control height */
    min-height: auto !important; /* Don't constrain minimum height */
    max-height: none !important; /* Let rows handle the sizing */
}

.resource-desc-gradio textarea:hover {
    border-color: #ccc !important;
}

.resource-desc-gradio textarea:focus {
    outline: none !important;
    box-shadow: none !important;

}

.resource-desc-gradio textarea::placeholder {
    color: #999 !important;
    font-style: italic !important
}

/* Show scrollbar only when content exceeds max-height */
.resource-desc-gradio textarea.scrollable {
    overflow-y: auto !important;
    scrollbar-width: auto !important; /* Firefox - normal width */
    -ms-overflow-style: auto !important; /* IE */
    padding: 4px 0px 4px 6px !important;
    max-height: none !important; /* Let rows handle sizing */
}

/* Ensure webkit scrollbar is visible for resource description */
.resource-desc-gradio textarea.scrollable::-webkit-scrollbar {
    width: 16px !important;
    display: block !important;
    cursor: default !important;
}

.resource-desc-gradio textarea.scrollable::-webkit-scrollbar-track {
    background: #f1f1f1;
    border: 3px solid transparent;
    background-clip: content-box;
    border-radius: 8px;
    margin-top: 15px;
    margin-right: 5px;
    cursor: default !important;
}

.resource-desc-gradio textarea.scrollable::-webkit-scrollbar-thumb {
    background: #999999;
    border: 3px solid transparent;
    background-clip: content-box;
    border-radius: 8px;
    cursor: default !important;
}

.resource-desc-gradio textarea.scrollable::-webkit-scrollbar-thumb:hover {
    background: #7a7a7a;
    cursor: default !important;
    border: 3px solid transparent !important;
    background-clip: content-box !important;
}

/* Collapsed state for resource description */
.resource-desc-gradio.collapsed textarea {
    overflow: hidden !important;
    height: auto !important; /* Let rows attribute control height */
    max-height: none !important; /* Remove max-height constraint */
    cursor: text !important;
}

/* Description expand button in resource description */
.resource-desc-gradio .desc-expand-btn {
    position: absolute;
    top: 0px;
    right: 3px;
    width: 14px;
    height: 20px;
    padding: 0;
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 12px;
    line-height: 20px;
    color: #999;
    display: none; /* Hidden by default */
    z-index: 10;
}

.resource-desc-gradio .desc-expand-btn:hover {
    color: #666;
}

.resource-desc-gradio .desc-expand-btn:focus {
    outline: none;
}

/* Rotate chevron for expanded state to match doc description */
.resource-desc-gradio:not(.collapsed) .desc-expand-btn {
    transform: rotate(180deg);
    top: 4px;
    right: 2px;
}

.resource-desc-gradio.collapsed .desc-expand-btn {
    transform: rotate(0deg);
    top: 2px; /* Match doc description positioning */
    right: 2px;
}*/


/* Resource filename styling */
.resource-filename {
    font-size: 9px !important;
    color: #666 !important;
    margin: 4px -6px -6px -6px !important; /* Extend to edges of container */
    padding: 4px 6px !important;
    font-family: monospace !important;
    line-height: 1.2 !important;
    background-color: #f5f5f5 !important; /* Same as resource-item background */
}

/* Target any child elements inside resource-filename */
.resource-filename * {
    font-size: inherit !important;
}

/* If Gradio wraps the text in a p or span */
.block.resource-filename div {
    font-size: 9px !important;
    margin: 0 !important;
    margin-left: 4px;
    margin-top: 4px;
    padding: 0 !important;
    text-align: left !important;
    color: #666 !important;
    font-family: monospace !important;
}

/* Gradio resource upload zone */
.resource-upload-gradio {
    margin-top: 4px !important;
    min-height: 32px !important;
    border: 1px dashed #4a9d9e !important;
    border-radius: 4px !important;
    background-color: #f8fafa !important;
    transition: all 0.3s ease !important;
}

.resource-upload-gradio:hover {
    border-color: #3a8d8e !important;
    background-color: #f0f9f9 !important;
}

.resource-upload-gradio.drag-over {
    border-color: #4a9d9e !important;
    background-color: #e8f5f5 !important;
}

/* Style the Gradio file upload component inside resource */
.resource-upload-gradio .wrap {
    min-height: 30px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 11px !important;
    color: #666 !important;
    padding: 4px !important;
}

.resource-upload-gradio .icon-wrap {
    width: 16px !important;
    height: 16px !important;
    margin-right: 4px !important;
}

/* Hide file preview in resource upload */
.resource-upload-gradio .file-preview {
    display: none !important;
}

/* Delete button for resources in panel */
.resource-delete {
    cursor: pointer;
    padding: 0 4px;
    font-weight: bold;
    color: #999;
    font-size: 16px; /* Bigger trash can icon */
    transition: color 0.2s ease;
    opacity: 0;
    flex-shrink: 0;
}

.resource-item:hover .resource-delete,
.resource-item-gradio:hover .resource-delete {
    opacity: 1;
}

.resource-delete:hover {
    color: #ff5252;
}

/* Gradio resource delete button styling */
.resource-delete-btn {
    position: absolute !important;
    top: 1px !important;
    right: 1px !important;
    width: 20px !important;
    height: 20px !important;
    min-width: 20px !important;
    min-height: 20px !important;
    padding: 0 !important;
    background-color: #f5f5f5 !important;
    border: 1px solid #d0d0d0 !important;
    border-radius: 3px !important;
    font-size: 14px !important;
    color: #333 !important;
    cursor: pointer !important;
    transition: opacity 0.2s ease, background-color 0.2s ease !important;
    opacity: 1 !important;
    z-index: 10 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Override Gradio button styles for delete button */
.resource-item-gradio .resource-delete-btn.svelte-1pjfiar,
.resource-item-gradio .resource-delete-btn {
    box-shadow: none !important;
    background-image: none !important;
    background-color: transparent !important;
}

.resource-delete-btn:hover {
    background-color: #ff6b6b !important;
    border-color: #ff5252 !important;
    color: white !important;
}

/* Ensure the button's parent column doesn't interfere */
.resource-item-gradio > .form > .wrap > .wrap > div:last-child {
    position: static !important;
    width: auto !important;
    height: auto !important;
}

/* Make the resource group relative positioned for absolute button */
.resource-item-gradio {
    position: relative !important;
    background: #f5f5f5 !important;
    overflow: visible !important; /* Allow button to extend outside */
}

/* Ensure all Gradio wrapper elements have the right background */
.resource-item-gradio > div,
.resource-item-gradio > .form,
.resource-item-gradio > .form > .wrap,
.resource-item-gradio > .form > .wrap > .wrap {
    background: #f5f5f5 !important;
}

/* Adjust the resource row to not interfere with absolute button */
.resource-row-gradio {
    background: #f5f5f5 !important;
}

/* Target any form elements inside resource items */
.resource-item-gradio .form {
    background: #f5f5f5 !important;
}

/* Resource description container */
.resource-description-container {
    position: relative;
    margin-top: 4px;
}

/* Resource panel description textarea */
.resource-panel-description {
    width: 100%;
    min-height: 32px; /* About 2 lines */
    max-height: 180px; /* About 10 lines with 11px font and 1.4 line height */
    padding: 4px 18px 4px 6px; /* Extra padding on right for button */
    border: 1px solid #e0e0e0;
    border-radius: 3px;
    font-size: 11px;
    line-height: 1.4 !important; /* Match document description */
    font-family: inherit;
    resize: none;
    overflow-y: hidden; /* Hide scrollbar by default */
    background: white;
    transition: height 0.1s ease;
    cursor: text;
    user-select: text;
}

/* Show scrollbar only when content exceeds max-height */
.resource-panel-description.scrollable {
    overflow-y: auto !important;
    scrollbar-width: auto !important; /* Firefox - normal width */
    -ms-overflow-style: auto !important; /* IE */
    padding-right: 4px;
}

/* Ensure webkit scrollbar is visible for resource description */
.resource-panel-description.scrollable::-webkit-scrollbar {
    width: 16px !important; /* Slightly narrower than doc description */
    display: block !important;
    cursor: default !important;
}

.resource-panel-description.scrollable::-webkit-scrollbar-track {
    background: #f1f1f1;
    border: 3px solid transparent; /* Less padding than doc description */
    background-clip: content-box;
    border-radius: 8px;
    margin-top: 15px; /* Leave space for chevron */
    margin-right: 3px;
    cursor: default !important;
}

.resource-panel-description.scrollable::-webkit-scrollbar-thumb {
    background: #999999;
    border: 3px solid transparent; /* Less padding than doc description */
    background-clip: content-box;
    border-radius: 8px;
    cursor: default !important;
}

.resource-panel-description.scrollable::-webkit-scrollbar-thumb:hover {
    background: #7a7a7a;
    cursor: default !important;
    border:3px solid transparent !important;
    background-clip: content-box !important;
}

/* Remove scrollbar buttons (arrows) */
.resource-panel-description.scrollable::-webkit-scrollbar-button {
    display: none;
}

.resource-panel-description:focus {
    outline: none;
    border-color: #e0e0e0; /* Keep same border color as default */
}

.resource-panel-description::placeholder {
    color: #999;
    font-style: italic;
}

/* Collapsed state for resource description */
.resource-description-container.collapsed .resource-panel-description {
    overflow: hidden !important;
    max-height: 32px !important; /* Exactly 2 lines */
}

/* Description expand button in resource panel */
.resource-description-container .desc-expand-btn {
    position: absolute;
    top: 2px;
    right: 3px;
    width: 14px;
    height: 16px;
    padding: 0;
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 12px;
    line-height: 16px;
    color: #999;
    display: none; /* Hidden by default */
    z-index: 10;
}

.resource-description-container .desc-expand-btn:hover {
    color: #666;
}

.resource-description-container .desc-expand-btn:focus {
    outline: none;
}

/* Rotate chevron for expanded state to match content blocks */
.resource-description-container:not(.collapsed) .desc-expand-btn {
    transform: rotate(180deg);
}

.resource-description-container.collapsed .desc-expand-btn {
    transform: rotate(0deg);
    /* Add your custom positioning here */
    top: -1px;
}



/* Drag and drop styles */
.block-resources.drag-over {
    border-color: #4a9d9e !important;
    background-color: #e8f5f5 !important;
    border-width: 1px !important;
}

/* Dropped resource styles */
.dropped-resource {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 8px;
    margin: 2px;
    background-color: #4a9d9e;
    border: 1px solid #4a9d9e;
    border-radius: 4px;
    font-size: 12px;
    color: white;
    cursor: default;
}

/* Remove hover effect on the dropped resource itself */
.dropped-resource:hover {
    background-color: #4a9d9e; /* Keep same as default */
    border-color: #4a9d9e; /* Keep same as default */
}

/* Style for the remove button */
.dropped-resource .remove-resource {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    padding: 0;
    margin-left: 4px;
    background-color: white;
    border: 1px solid #ddd; /* Light gray border to make white button visible */
    border-radius: 3px;
    color: #333;
    font-size: 16px;
    font-weight: normal;
    font-style: normal;
    cursor: pointer;
}

/* Hover effect on X button - matches delete button behavior */
.dropped-resource .remove-resource:hover {
    background-color: #ff6b6b;
    border-color: #ff5252;
    color: white;
    cursor: pointer;
}


/* Load resource button */
.load-resource-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 14px;
    padding: 0 4px;
    opacity: 0.6;
    transition: opacity 0.2s ease;
}

.load-resource-btn:hover {
    opacity: 1;
}

/* Resource container for AI blocks with descriptions */
.dropped-resource-container {
    margin-bottom: 8px;
    padding: 4px;
    background-color: #f8f8f8;
    border-radius: 3px;
    text-align: left;
}

.dropped-resource-container .dropped-resource {
    display: inline-block;
    width: auto;
    margin-bottom: 4px;
    text-align: left;
}

.resource-description {
    width: 100%;
    padding: 4px 8px;
    margin-top: 4px;
    border: 1px solid #ddd;
    border-radius: 3px;
    font-size: 11px;
    font-style: italic;
    background-color: white;
    transition: border-color 0.2s ease;
}

.resource-description:focus {
    outline: none;
    border-color: #4a9d9e;
}

.resource-description::placeholder {
    color: #999;
}



/* Resource upload zone styles */
.resource-upload-zone {
    margin-top: 8px;
    padding: 8px;
    border: 1px dashed #4a9d9e;
    border-radius: 8px;
    background-color: #f8fafa;
    text-align: center;
    position: relative;
    min-height: 32px;
    transition: all 0.3s ease;
    cursor: pointer;
}

.resource-upload-zone:hover {
    border-color: #3a8d8e;
    background-color: #f0f9f9;
}

.resource-upload-zone.drag-over {
    border-color: #4a9d9e;
    background-color: #e8f5f5;
    border-width: 1px;
}

.resource-upload-zone .upload-text {
    font-size: 11px;
    color: #666;
    pointer-events: none;
}

.resource-upload-zone .resource-file-input {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
}

.resource-upload-zone.upload-success {
    background-color: #d4edda;
    border-color: #28a745;
}

.resource-upload-zone.upload-success .upload-text {
    color: #155724;
    font-weight: bold;
}


/* Workspace */
.workspace-col {
    width: 100% !important;
    min-width: 500px !important;
    max-width: 100% !important;
    margin-left: 5px !important;
    margin-right: 5px !important;
    gap: 8px !important;
}
.workspace-display {
    height: 680px !important;
    color: #bbbbc2 !important;
    background-color: white !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e5e5;
    border-radius: 8px !important;
    overflow-y: auto; /* Show scrollbar only when needed */
    overflow-x: hidden;
}

/* Remove the rules that hide all scrollbars inside workspace - we want to show them when needed */

/* Workspace - Content block add buttons */
.add-section-btn {
    width: 120px !important;
    min-width: 120px !important;
    max-width: 120px !important;
    height: 30px !important;
    background-color: #4a9d9e !important;
    border: 1px solid #4a9d9e !important;
    color: white !important;
    font-weight: bold !important;
}
.add-section-btn:hover {
    background-color: #3a8d8e !important;
    border-color: #3a8d8e !important;
}

/* Workspace collapse/expand all buttons - match New button style */
.workspace-collapse-btn {
    width: 30px !important;
    min-width: 30px !important;
    max-width: 30px !important;
    height: 30px !important;
    padding: 0 !important;
    background-color: #ffffff !important;
    border: 1px solid #d0d0d0 !important;
    border-radius: 4px !important;
    font-size: 16px !important;
    line-height: 30px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    color: #333333 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.workspace-collapse-btn:hover {
    background-color: #f5f5f5 !important;
    border-color: #b0b0b0 !important;
    color: #333333 !important;
}

.square-btn-row {
    gap: 8px !important;
}

/* Specific styling for collapse all (rotated to point up like expanded blocks) */
.collapse-all-btn {
    font-weight: 500 !important;
    transform: rotate(180deg) !important;
    position: relative !important;
    padding-bottom: 7px !important;  /* This becomes padding-top after rotation */
    padding-top: 0px !important;
    line-height: 1 !important;
}

/* Specific styling for expand all (points down like collapsed blocks) */
.expand-all-btn {
    font-weight: 500 !important;
    transform: rotate(0deg) !important;
    position: relative !important;
    padding-bottom: 6px !important;  /* Push the chevron up */
    padding-top: 0px !important;
    line-height: 1 !important;
}

/* Secondary workspace button - white with grey border */
.secondary-workspace-btn {
    width: 120px !important;
    min-width: 120px !important;
    max-width: 120px !important;
    height: 30px !important;
    background-color: #ffffff !important;
    border: 1px solid #d0d0d0 !important;
    color: #666666 !important;
    font-weight: bold !important;
}
.secondary-workspace-btn:hover {
    background-color: #f5f5f5 !important;
    border-color: #b0b0b0 !important;
    color: #555555 !important;
}

/* Workspace - Content block styling */
.blocks-container {
    display: flex;
    flex-direction: column;
    gap: 5px;
}
.blocks-container .html-container {
    padding: 40px !important;
    font-style: italic !important;
}

.content-block {
    background-color: white;
    border-radius: 6px;
    border: 1px solid #e0e0e0;
    padding: 10px;
    position: relative;
    transition: box-shadow 0.2s ease, margin-left 0.2s ease, width 0.2s ease, background-color 0.2s ease;
}

.content-block:hover {
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}


/* Indentation levels - using margin for visual indent but keeping arrows fixed */
.content-block[data-indent="0"] {
    margin-left: 0;
    width: 100%;
}
.content-block[data-indent="1"] {
    margin-left: 30px;
    width: calc(100% - 30px);
}
.content-block[data-indent="2"] {
    margin-left: 60px;
    width: calc(100% - 60px);
}
.content-block[data-indent="3"] {
    margin-left: 90px;
    width: calc(100% - 90px);
}
.content-block[data-indent="4"] {
    margin-left: 120px;
    width: calc(100% - 120px);
}
.content-block[data-indent="5"] {
    margin-left: 150px;
    width: calc(100% - 150px);
}

/* Indent controls */
.indent-controls {
    position: absolute;
    top: 0px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    opacity: 0;
    transition: opacity 0.2s ease;
    padding-top: 7px;
    padding-bottom: 7px;
    padding-left: 2px;
}

/* Adjust indent control position based on indent level to keep them fixed */
.content-block[data-indent="0"] .indent-controls { left: -35px; padding-right: 35px;}
.content-block[data-indent="1"] .indent-controls { left: -65px; padding-right: 65px;}
.content-block[data-indent="2"] .indent-controls { left: -95px; padding-right: 95px;}
.content-block[data-indent="3"] .indent-controls { left: -125px; padding-right: 125px;}
.content-block[data-indent="4"] .indent-controls { left: -155px; padding-right: 155px;}
.content-block[data-indent="5"] .indent-controls { left: -185px; padding-right: 185px;}

.content-block:hover .indent-controls,
.content-block:focus-within .indent-controls {
    opacity: 1;
}

.indent-btn {
    width: 20px;
    height: 20px;
    padding: 0;
    border: 1px solid #ddd;
    background-color: #f5f5f5;
    border-radius: 3px;
    font-size: 10px;
    line-height: 1;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
}

.indent-btn:hover {
    background-color: #e0e0e0;
    outline: none;
}

.indent-btn:focus {
    outline: none;
}

.indent-btn.outdent {
    color: #666;
}

.indent-btn.indent {
    color: #666;
}

/* Placeholder to maintain spacing when button is hidden */
.indent-btn-placeholder {
    width: 20px;
    height: 20px;
}

.ai-block {
    border-left: 3px solid #4a9d9e !important;
}
.ai-block textarea {
    width: 100%;
    min-height: 120px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 10px;
    font-size: 14px;
    resize: none; /* Disable manual resize since we auto-expand */
    background: white;
    outline: none;
    overflow-y: hidden; /* Hide vertical scrollbars */
    overflow-x: hidden; /* Hide horizontal scrollbars */
    transition: height 0.1s ease;
    box-sizing: border-box;
}
.ai-block .block-resources {
    min-height: 40px;
    border: 1px dashed #4a9d9e;
    border-radius: 4px;
    padding: 8px;
    text-align: center;
    color: #999;
    font-size: 12px;
    background-color: #f8f8f8;
    cursor: default;
}

.text-block {
    border-left: 3px solid #b8b8b8 !important;
}
.text-block textarea {
    width: 100%;
    min-height: 120px;
    max-height: none; /* Remove height limit */
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 10px;
    font-size: 14px;
    resize: none; /* Keep manual resize disabled */
    background: white;
    outline: none;
    overflow-y: auto; /* Show scrollbars when needed */
    overflow-x: hidden; /* Hide horizontal scrollbars */
    transition: height 0.1s ease;
    box-sizing: border-box;
}
.text-block .block-resources {
    min-height: 40px;
    border: 1px dashed #d0d0d0;
    border-radius: 4px;
    padding: 8px;
    text-align: center;
    color: #999;
    font-size: 12px;
    background-color: #f8f8f8;
    cursor: default;
}

/* Heading input styles for AI and Text blocks - inline version */
.block-heading-inline {
    flex: 1;
    font-size: 16px;
    font-weight: bold;
    border: none;
    outline: none;
    background: transparent;
    padding: 4px 8px;
    margin: 0 24px 0 0;
    color: #333;
    transition: background-color 0.2s ease;
}

.block-heading-inline:focus {
    background-color: rgba(0, 0, 0, 0.05);
    border-radius: 4px;
}

.block-heading-inline::placeholder {
    color: #bbbbc2;
    font-weight: normal;
}

/* Update block header to use flexbox for proper alignment */
.block-header {
    display: flex;
    align-items: center;
    gap: 0;
    min-height: 36px;
    position: relative;
}

.delete-btn {
    position: absolute;
    top: 6px;
    right: -30px; /* Move outside the block into the margin */
    width: 20px;
    height: 20px;
    padding: 0;
    background-color: #f5f5f5;
    border: 1px solid #d0d0d0;
    border-radius: 3px;
    font-size: 14px;
    line-height: 1;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.2s ease, background-color 0.2s ease;
    z-index: 10;
}

.add-btn {
    position: absolute;
    top: 30px;  /* 10px (delete button top) + 20px (delete button height) + 5px gap */
    right: -30px; /* Same as delete button - outside the block */
    width: 20px;
    height: 20px;
    padding: 0;
    background-color: #f5f5f5;
    border: 1px solid #d0d0d0;
    border-radius: 3px;
    font-size: 14px;
    line-height: 1;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.2s ease, background-color 0.2s ease;
    z-index: 10;
}

.content-block:hover .delete-btn,
.content-block:hover .add-btn,
.content-block:focus-within .delete-btn,
.content-block:focus-within .add-btn {
    opacity: 1;
}

.delete-btn:hover {
    background-color: #ff6b6b;
    border-color: #ff5252;
    color: white;
}

.add-btn:hover {
    background-color: #e0e0e0;
    border-color: #999;
}

/* Block tabs styling */
.block-tabs {
    display: inline-flex;
    margin-bottom: 1px; /* Overlap with textarea border */
    position: relative;
    top: 1px;
}

.block-tab {
    width: 42px;
    height: 24px;
    padding: 3px 10px;
    background-color: #f5f5f5;
    border: 1px solid #e0e0e0;
    border-bottom: none;
    cursor: pointer;
    font-size: 11px;
    font-weight: 500;
    color: #666;
    transition: all 0.2s ease;
    margin-right: -1px; /* Overlap borders */
}


.block-tab.active:first-child {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-bottom: 1px solid white;
    color: #4a9d9e;
    font-weight: 600;
    position: relative;
    z-index: 1;
}

.block-tab:first-child {
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-bottom: 0;
    border-bottom: 1px solid #e0e0e0;
    color: #4a9d9e;
}

.block-tab:hover:not(.active) {
    background-color: #eeeeee;
    color: #333;
}

/* Keep teal color for AI tab on hover */
.block-tab:first-child:hover:not(.active) {
    color: #4a9d9e;
}


.block-tab.active:last-child {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-bottom: 1px solid white;
    color: #666;
    font-weight: 600;
    position: relative;
    z-index: 1;
}

.block-tab:last-child {
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 0;
    border-bottom: 1px solid #e0e0e0;
}
.block-tab:last-child:hover:not(.active) {
    background-color: #eeeeee;
    color: #333;
}

/* Update textarea styling to connect with tabs */
.ai-block .block-tabs + textarea,
.text-block .block-tabs + textarea {
    margin-top: -1px;
}

/* Remove top-left border radius for AI and Text block textareas to align with tabs */
.ai-block .block-tabs + textarea,
.text-block .block-tabs + textarea {
    border-top-left-radius: 0;
}

/* Empty blocks message */
.empty-blocks-message {
    color: #bbbbc2;
    text-align: left;

}

/* Collapsible blocks */
.collapse-btn {
    position: absolute;
    top: 6px;
    right: 6px;
    width: 20px;
    height: 20px;
    padding: 0;
    background-color: #f5f5f5;
    border: 1px solid #d0d0d0;
    border-radius: 3px;
    font-size: 12px;
    line-height: 20px;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.2s ease, background-color 0.2s ease, color 0.2s ease;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #2e2e2e;
}

.content-block:hover .collapse-btn,
.content-block:focus-within .collapse-btn {
    opacity: 1;
}

.collapse-btn:hover {
    background-color: #e0e0e0;
    border-color: #999;
    color: #333;
}

.collapse-icon {
    display: inline-block;
    transition: transform 0.2s ease;
    font-family: Arial, sans-serif;
    font-weight: 600;
    position: relative;
    top: 1px;  /* Fine-tune vertical position */
}

.collapsed .collapse-icon {
    transform: rotate(0deg);  /* Point down when collapsed */
    top: -1px;
    font-weight: 400;
}

.content-block:not(.collapsed) .collapse-icon {
    transform: rotate(180deg);  /* Point up when expanded */
}

.content-block.collapsed {
    min-height: auto;
}

.content-block.collapsed .block-content {
    display: none;
}

.block-content {
    max-height: 0;
    opacity: 0;
    overflow: hidden;
    transition: max-height 0.3s ease, opacity 0.2s ease;
}

.block-content.show {
    max-height: none; /* Remove height limit to allow full content */
    opacity: 1;
    padding-top: 10px;
}

.block-content textarea::placeholder {
    color: #bbbbc2;
}

/* Generate Document */
.generate-col {
    width: 100% !important;
    min-width: 500px !important;  /* Match workspace panel minimum */
    max-width: 100% !important;
    margin-left: 5px !important;
    gap: 8px !important;
}
.generate-display {
    height: 680px !important;
    background-color: white !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e5e5;
    border-radius: 8px !important;
    overflow-y: auto; /* Show scrollbar only when needed */
    overflow-x: hidden;
    padding: 40px !important;
    font-size: 14px !important;
    color: #bbbbc2 !important;
}

/* Specific targeting for generated content */
.generated-content em {
    color: #bbbbc2;  /* --neutral-400: #bbbbc2 used for placeholders in gradio */
}

/* Hide scrollbar for HTML content (loading state) but keep for Markdown */
.generate-display .gradio-html,
.generate-display .gradio-html *,
.generated-content {
    overflow: hidden !important;
    -ms-overflow-style: none !important;  /* IE and Edge */
    scrollbar-width: none !important;  /* Firefox */
}

.generate-display .gradio-html::-webkit-scrollbar,
.generate-display .gradio-html *::-webkit-scrollbar,
.generated-content::-webkit-scrollbar {
    display: none !important;  /* Chrome, Safari and Opera */
}

/* Generate Document - buttons*/
.generate-btn-row {
    gap: 8px !important;
}

.generate-btn {
    width: 120px !important;
    min-width: 120px !important;
    max-width: 120px !important;
    height: 30px !important;
    background-color: #4a9d9e !important;
    border: 1px solid #4a9d9e !important;
    color: white !important;
    font-weight: bold !important;
}

.generate-btn:hover {
    background-color: #3a8d8e !important;
    border-color: #3a8d8e !important;
}

.download-btn {
    width: 120px !important;
    min-width: 120px !important;
    max-width: 120px !important;
    height: 30px !important;

}

/* Footer styling - change text color */
footer button,
footer a {
    color: #27272a !important;
}

/* Gradio resource item drag and drop styles */
.resource-item-gradio {
    cursor: grab !important;
    transition: all 0.2s ease;
}

.resource-item-gradio:hover {
    background: #f0f0f0;
    cursor: grab !important;
}

.resource-item-gradio:active {
    cursor: grabbing !important;
}

.resource-item-gradio.dragging {
    opacity: 0.5;
    cursor: grabbing !important;
    background: #e0e0e0;
}

/* Global cursor while dragging */
body.dragging-resource,
body.dragging-resource * {
    cursor: grabbing !important;
}

/* Ensure all elements show grabbing cursor during drag, except drop zones */
body.dragging-resource *:not(.no-drop):not(.block-resources) {
    cursor: grabbing !important;
}

/* Drag and drop styles - matching HTML version */
.block-resources.drag-over {
    border-color: #4a9d9e !important;
    background-color: #e8f5f5 !important;
    border-width: 1px !important;
    cursor: copy !important;
}

/* Show copy cursor on drop zones when hovering during drag */
body.dragging-resource .block-resources:hover {
    cursor: copy !important;
}

/* Show copy cursor when actively dragging over */
body.dragging-resource .block-resources.drag-over {
    cursor: copy !important;
}

/* Show not-allowed cursor when dragging over invalid drop targets */
textarea.no-drop,
input.no-drop,
.resource-upload-gradio.no-drop,
.no-drop {
    cursor: not-allowed !important;
}

/* Also style file upload zones to show they're not valid drop targets */
.resource-upload-gradio.no-drop {
    opacity: 0.6;
}

/* Start tab error message styling */
.start-error-message {
    margin-top: 8px;
    animation: slideDown 0.3s ease-out;
}

.file-upload-warning .html-container {
    padding: 0px;
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}


=== File: apps/document-generator/document_generator_app/static/images/evergreen_content-removebg-preview.jpg ===
[ERROR reading file: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte]


=== File: apps/document-generator/document_generator_app/static/images/smart_regeneration-removebg-preview.jpg ===
[ERROR reading file: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte]


=== File: apps/document-generator/document_generator_app/static/images/template_control-removebg-preview.jpg ===
[ERROR reading file: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte]


=== File: apps/document-generator/document_generator_app/static/js/script.js ===
// Document Builder JavaScript
console.log('🚀 JavaScript file loaded successfully!');

// Auto-resize textarea function
function autoResizeTextarea(textarea) {
    console.log('Auto-resizing textarea:', textarea);
    textarea.style.height = 'auto';
    const newHeight = Math.max(120, textarea.scrollHeight);
    textarea.style.height = newHeight + 'px';
    console.log('Set textarea height to:', newHeight + 'px', 'scrollHeight:', textarea.scrollHeight);
}

// Setup auto-resize for all text block textareas
function setupTextareaAutoResize() {
    const textareas = document.querySelectorAll('.text-block textarea');
    textareas.forEach(textarea => {
        // Auto-resize on input
        textarea.addEventListener('input', function() {
            autoResizeTextarea(this);
        });
        
        // Initial resize in case there's already content
        autoResizeTextarea(textarea);
    });
}

// Run setup when DOM changes (new blocks added)
const textareaObserver = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'childList') {
            setupTextareaAutoResize();
        }
    });
});

// Start observing
textareaObserver.observe(document.body, {
    childList: true,
    subtree: true
});

// Initial setup
document.addEventListener('DOMContentLoaded', setupTextareaAutoResize);

// Add warning when user tries to leave the page
// Since there's no autosave, always warn users about losing their work
window.addEventListener('beforeunload', function (e) {
    // Custom message (note: most modern browsers show a generic message instead)
    const confirmationMessage = 'Warning: There is no autosave. If you leave this page, all your work will be lost. Make sure to save your document before leaving.';
    
    // Prevent default and set return value for modern browsers
    e.preventDefault();
    e.returnValue = confirmationMessage;
    
    // Return message for older browsers
    return confirmationMessage;
});

function refresh() {
    console.log('refresh() called');
    const url = new URL(window.location);
    elements = document.getElementsByClassName("dark")
    console.log('Found dark elements:', elements.length);
    if (elements.length != 0) {
        console.log('Dark elements:', elements)
        elements[0].classList.remove("dark");
        console.log('Refreshing in light mode - removed dark class');
    }
}


// Toggle debug panel visibility
function toggleDebugPanel() {
    console.log('toggleDebugPanel called');
    const content = document.getElementById('debug-panel-content');
    const icon = document.getElementById('debug-collapse-icon');

    console.log('Debug panel content element:', content);
    console.log('Current display style:', content ? content.style.display : 'content not found');
    console.log('Icon element:', icon);

    if (content) {
        if (content.style.display === 'none' || content.style.display === '') {
            console.log('Opening debug panel');
            content.style.display = 'block';
            if (icon) {
                icon.textContent = '⌵';
                icon.style.transform = 'rotate(180deg)';  // Rotate down chevron to point up
            }
        } else {
            console.log('Closing debug panel');
            content.style.display = 'none';
            if (icon) {
                icon.textContent = '⌵';
                icon.style.transform = 'rotate(0deg)';  // Normal down chevron
            }
        }
    } else {
        console.error('Debug panel content element not found!');
    }
}

// No longer needed - using Gradio's native file upload component

// Process steps hover interaction
document.addEventListener('DOMContentLoaded', function() {
    // Process step visuals
    const stepVisuals = {
        1: {
            svg: `<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
                    <!-- Document with AI sparkle -->
                    <rect x="100" y="50" width="200" height="250" rx="8" fill="#f0f9f9" stroke="#4a9d9e" stroke-width="2"/>
                    <rect x="120" y="80" width="160" height="8" rx="4" fill="#4a9d9e" opacity="0.3"/>
                    <rect x="120" y="100" width="140" height="8" rx="4" fill="#4a9d9e" opacity="0.3"/>
                    <rect x="120" y="120" width="150" height="8" rx="4" fill="#4a9d9e" opacity="0.3"/>
                    <g transform="translate(250, 70)">
                        <path d="M0,-10 L3,-3 L10,0 L3,3 L0,10 L-3,3 L-10,0 L-3,-3 Z" fill="#4a9d9e" opacity="0.8"/>
                    </g>
                    <rect x="120" y="150" width="160" height="40" rx="4" fill="#e8f5f5" stroke="#4a9d9e" stroke-width="1"/>
                    <rect x="120" y="200" width="160" height="40" rx="4" fill="#e8f5f5" stroke="#4a9d9e" stroke-width="1"/>
                    <rect x="120" y="250" width="160" height="40" rx="4" fill="#e8f5f5" stroke="#4a9d9e" stroke-width="1"/>
                </svg>`,
            caption: "Your document takes shape with AI assistance"
        },
        2: {
            svg: `<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
                    <!-- Document with edit icon and files -->
                    <rect x="80" y="50" width="180" height="220" rx="8" fill="#f0f9f9" stroke="#4a9d9e" stroke-width="2"/>
                    <!-- Edit pencil -->
                    <g transform="translate(240, 60)">
                        <path d="M0,20 L5,15 L20,0 L25,5 L10,20 Z" fill="#4a9d9e"/>
                        <rect x="0" y="20" width="5" height="5" fill="#4a9d9e"/>
                    </g>
                    <!-- File icons -->
                    <rect x="280" y="80" width="40" height="50" rx="4" fill="#e8f5f5" stroke="#4a9d9e" stroke-width="1"/>
                    <rect x="280" y="140" width="40" height="50" rx="4" fill="#e8f5f5" stroke="#4a9d9e" stroke-width="1"/>
                    <!-- Arrow from files to doc -->
                    <path d="M280,105 L260,150" stroke="#4a9d9e" stroke-width="2" marker-end="url(#arrowhead)"/>
                    <defs>
                        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                            <polygon points="0 0, 10 3.5, 0 7" fill="#4a9d9e"/>
                        </marker>
                    </defs>
                </svg>`,
            caption: "Edit content and update resources as needed"
        },
        3: {
            svg: `<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
                    <!-- Multiple export formats -->
                    <rect x="50" y="100" width="80" height="100" rx="8" fill="#e8f5f5" stroke="#4a9d9e" stroke-width="2"/>
                    <text x="90" y="155" text-anchor="middle" fill="#4a9d9e" font-size="14" font-weight="bold">PDF</text>
                    <rect x="160" y="100" width="80" height="100" rx="8" fill="#e8f5f5" stroke="#4a9d9e" stroke-width="2"/>
                    <text x="200" y="155" text-anchor="middle" fill="#4a9d9e" font-size="14" font-weight="bold">DOCX</text>
                    <rect x="270" y="100" width="80" height="100" rx="8" fill="#e8f5f5" stroke="#4a9d9e" stroke-width="2"/>
                    <text x="310" y="155" text-anchor="middle" fill="#4a9d9e" font-size="14" font-weight="bold">MD</text>
                    <!-- Export arrow -->
                    <path d="M200,50 L200,80" stroke="#4a9d9e" stroke-width="3" marker-end="url(#arrowhead2)"/>
                    <defs>
                        <marker id="arrowhead2" markerWidth="10" markerHeight="7" refX="5" refY="7" orient="auto">
                            <polygon points="0 0, 10 3.5, 0 7" fill="#4a9d9e"/>
                        </marker>
                    </defs>
                </svg>`,
            caption: "Generate and export in multiple formats"
        }
    };

    // Function to update visual
    function updateProcessVisual(stepNumber) {
        const visualContent = document.querySelector('.visual-content');
        if (visualContent && stepVisuals[stepNumber]) {
            visualContent.innerHTML = stepVisuals[stepNumber].svg +
                `<p class="visual-caption">${stepVisuals[stepNumber].caption}</p>`;
        }
    }

    // Set up hover listeners with delay
    setTimeout(() => {
        const steps = document.querySelectorAll('.start-process-step-vertical');
        steps.forEach((step, index) => {
            step.addEventListener('mouseenter', () => {
                // Remove active class from all steps
                steps.forEach(s => s.classList.remove('active'));
                // Add active class to hovered step
                step.classList.add('active');
                // Update visual
                updateProcessVisual(index + 1);
            });
        });
    }, 1000);
    
    // Setup resource description auto-expand
    setupResourceDescriptionAutoExpand();
});

// Setup auto-expand for resource description textareas
function setupResourceDescriptionAutoExpand() {
    console.log('🔧 Setting up resource description auto-expand...');
    
    // Find all existing resource description textareas
    const resourceDescTextareas = document.querySelectorAll('.resource-desc-gradio textarea');
    console.log(`🔧 Found ${resourceDescTextareas.length} resource description textareas`);
    
    resourceDescTextareas.forEach(textarea => {
        setupSingleResourceDescTextarea(textarea);
    });
    
    // Use MutationObserver to catch dynamically added resource descriptions
    const resourceDescObserver = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    // Only look for resource desc textareas specifically
                    const newTextareas = node.querySelectorAll ? 
                        node.querySelectorAll('.resource-desc-gradio textarea') : 
                        [];
                    
                    newTextareas.forEach(textarea => {
                        if (!textarea.dataset.autoExpandSetup) {
                            console.log('Setting up auto-expand for new resource description textarea');
                            setupSingleResourceDescTextarea(textarea);
                        }
                    });
                    
                    // Also check if the node itself is a resource desc textarea
                    if (node.matches && node.matches('.resource-desc-gradio textarea') && !node.dataset.autoExpandSetup) {
                        console.log('Setting up auto-expand for new resource description textarea (direct match)');
                        setupSingleResourceDescTextarea(node);
                    }
                }
            });
        });
    });
    
    // Start observing, but be more specific about what we watch
    const resourcePanel = document.querySelector('.resources-panel') || document.body;
    resourceDescObserver.observe(resourcePanel, {
        childList: true,
        subtree: true
    });
}

// Setup auto-expand for a single resource description textarea
function setupSingleResourceDescTextarea(textarea) {
    if (textarea.dataset.autoExpandSetup) {
        console.log('🔧 Resource description textarea already setup, skipping');
        return; // Already setup
    }
    
    textarea.dataset.autoExpandSetup = 'true';
    console.log('🔧 Setting up auto-expand for resource description textarea:', textarea);
    
    // Initial sizing
    autoExpandResourceDescription(textarea);
    
    // Add event listeners
    textarea.addEventListener('input', () => {
        autoExpandResourceDescription(textarea);
    });
    
    textarea.addEventListener('paste', () => {
        // Delay to allow paste content to be processed
        setTimeout(() => {
            autoExpandResourceDescription(textarea);
        }, 10);
    });
}

// Expandable input section - try multiple approaches
console.log('Script loaded - setting up expandable section');

// Function to set up the expandable behavior
function setupExpandableInput() {
    console.log('=== EXPANDABLE SETUP DEBUG ===');
    console.log('Attempting to set up expandable input...');

    // Debug: Check for start-prompt-input element
    const startPromptContainer = document.getElementById('start-prompt-input');
    console.log('start-prompt-input container:', startPromptContainer);
    
    if (startPromptContainer) {
        const textareas = startPromptContainer.querySelectorAll('textarea');
        const inputs = startPromptContainer.querySelectorAll('input');
        console.log('Found textareas in container:', textareas.length, textareas);
        console.log('Found inputs in container:', inputs.length, inputs);
    }

    // Try multiple selectors for the prompt input
    const promptInput1 = document.querySelector('#start-prompt-input textarea');
    const promptInput2 = document.querySelector('#start-prompt-input input');
    const promptInput3 = document.querySelector('[id*="start-prompt"] textarea');
    const promptInput4 = document.querySelector('[id*="start-prompt"] input');
    
    console.log('Selector #start-prompt-input textarea:', promptInput1);
    console.log('Selector #start-prompt-input input:', promptInput2);
    console.log('Selector [id*="start-prompt"] textarea:', promptInput3);
    console.log('Selector [id*="start-prompt"] input:', promptInput4);
    
    const promptInput = promptInput1 || promptInput2 || promptInput3 || promptInput4;
    console.log('Final selected promptInput:', promptInput);

    // Debug: Check for expandable section
    const expandableSection = document.getElementById('start-expandable-section');
    console.log('start-expandable-section:', expandableSection);
    
    if (!expandableSection) {
        const allExpandableElements = document.querySelectorAll('[id*="expandable"]');
        console.log('All elements with "expandable" in id:', allExpandableElements);
        const allStartElements = document.querySelectorAll('[id*="start"]');
        console.log('All elements with "start" in id:', allStartElements);
    }

    if (promptInput && expandableSection) {
        console.log('✓ Found both elements - setting up event listeners');
        console.log('promptInput element type:', promptInput.tagName);
        console.log('expandableSection element type:', expandableSection.tagName);
        
        // Debug: Check current height of prompt input
        const currentHeight = window.getComputedStyle(promptInput).height;
        const currentScrollHeight = promptInput.scrollHeight;
        console.log(`📏 Main input current height: ${currentHeight}, scrollHeight: ${currentScrollHeight}px, content length: ${promptInput.value.length}`);

        // Expand on focus
        promptInput.addEventListener('focus', () => {
            console.log('✓ Input focused - expanding');
            expandableSection.classList.add('expanded');
            // Remove inline styles to let CSS handle the transition
            expandableSection.style.removeProperty('display');
            expandableSection.style.removeProperty('opacity');
            // Add class to card for styling
            const card = document.querySelector('.start-input-card');
            if (card) card.classList.add('has-expanded');
            
            // Replace file upload text after expansion
            setTimeout(() => {
                const draftFileUpload = document.querySelector('.start-file-upload-dropzone');
                if (draftFileUpload) {
                    const wrapDivs = draftFileUpload.querySelectorAll('.wrap');
                    wrapDivs.forEach(wrapDiv => {
                        if (wrapDiv.textContent.includes('Drop File Here')) {
                            wrapDiv.childNodes.forEach(node => {
                                if (node.nodeType === Node.TEXT_NODE && node.textContent.includes('Drop File Here')) {
                                    console.log('✅ Replacing "Drop File Here" on focus expansion');
                                    node.textContent = node.textContent.replace('Drop File Here', 'Drop Word or Text File Here');
                                }
                            });
                        }
                    });
                }
            }, 100);
        });

        // Also expand on click
        promptInput.addEventListener('click', () => {
            console.log('✓ Input clicked - current expanded state:', expandableSection.classList.contains('expanded'));
            if (!expandableSection.classList.contains('expanded')) {
                console.log('✓ Input clicked - expanding');
                expandableSection.classList.add('expanded');
                // Remove inline styles to let CSS handle the transition
                expandableSection.style.removeProperty('display');
                expandableSection.style.removeProperty('opacity');
                // Add class to card for styling
                const card = document.querySelector('.start-input-card');
                if (card) card.classList.add('has-expanded');
                
                // Replace file upload text after expansion
                setTimeout(() => {
                    const draftFileUpload = document.querySelector('.start-file-upload-dropzone');
                    if (draftFileUpload) {
                        const wrapDivs = draftFileUpload.querySelectorAll('.wrap');
                        wrapDivs.forEach(wrapDiv => {
                            if (wrapDiv.textContent.includes('Drop File Here')) {
                                wrapDiv.childNodes.forEach(node => {
                                    if (node.nodeType === Node.TEXT_NODE && node.textContent.includes('Drop File Here')) {
                                        console.log('✅ Replacing "Drop File Here" on click expansion');
                                        node.textContent = node.textContent.replace('Drop File Here', 'Drop Word or Text File Here');
                                    }
                                });
                            }
                        });
                    }
                }, 100);
            } else {
                console.log('✓ Input clicked - already expanded');
            }
        });

        // Function to expand the card
        function expandCard() {
            console.log('Expanding card');
            expandableSection.classList.add('expanded');
            // Remove inline styles to let CSS handle the transition
            expandableSection.style.removeProperty('display');
            expandableSection.style.removeProperty('opacity');
            // Add class to card for styling
            const card = document.querySelector('.start-input-card');
            if (card) card.classList.add('has-expanded');
            
            // Replace file upload text after expansion
            setTimeout(() => {
                const draftFileUpload = document.querySelector('.start-file-upload-dropzone');
                if (draftFileUpload) {
                    const wrapDivs = draftFileUpload.querySelectorAll('.wrap');
                    wrapDivs.forEach(wrapDiv => {
                        if (wrapDiv.textContent.includes('Drop File Here')) {
                            wrapDiv.childNodes.forEach(node => {
                                if (node.nodeType === Node.TEXT_NODE && node.textContent.includes('Drop File Here')) {
                                    console.log('✅ Replacing "Drop File Here" on expandCard()');
                                    node.textContent = node.textContent.replace('Drop File Here', 'Drop Word or Text File Here');
                                }
                            });
                        }
                    });
                }
            }, 100);
        }

        // Expand when example buttons are clicked
        const exampleButtons = document.querySelectorAll('.start-example-btn');
        exampleButtons.forEach(button => {
            button.addEventListener('click', () => {
                console.log('Example button clicked - expanding card');
                // Small delay to ensure the content is loaded first
                setTimeout(expandCard, 100);
            });
        });

        // Collapse when clicking outside
        document.addEventListener('click', (e) => {
            const inputCard = document.querySelector('.start-input-card');
            const expandableArea = document.getElementById('start-expandable-section');
            const isClickInInput = inputCard && inputCard.contains(e.target);
            const isClickInExpandable = expandableArea && expandableArea.contains(e.target);
            const isExampleButton = e.target.closest('.start-example-btn');
            const isRemoveButton = e.target.closest('.remove-resource');

            console.log('✓ Click outside check:', {
                target: e.target.tagName + (e.target.className ? '.' + e.target.className : ''),
                isClickInInput,
                isClickInExpandable,
                isExampleButton: !!isExampleButton,
                isRemoveButton: !!isRemoveButton,
                currentlyExpanded: expandableSection.classList.contains('expanded')
            });

            // Always collapse when clicking outside, unless it's a remove resource button
            if (!isClickInInput && !isClickInExpandable && !isExampleButton && !isRemoveButton) {
                console.log('✓ Clicking outside - collapsing');
                expandableSection.classList.remove('expanded');
                // Remove inline styles to let CSS handle the transition
                expandableSection.style.removeProperty('display');
                expandableSection.style.removeProperty('opacity');
                // Remove class from card
                const card = document.querySelector('.start-input-card');
                if (card) card.classList.remove('has-expanded');
            } else {
                console.log('✓ Click inside or on special element - not collapsing');
            }
        });

        return true;
    } else {
        console.log('✗ Missing elements:');
        console.log('  promptInput:', !!promptInput);
        console.log('  expandableSection:', !!expandableSection);
        console.log('=== END EXPANDABLE SETUP DEBUG ===');
        return false;
    }
}

// Try to set up expandable input with exponential backoff
let expandableSetupAttempts = 0;
const maxExpandableAttempts = 4;

function trySetupExpandableInput() {
    console.log('🔄 trySetupExpandableInput() called, attempt:', expandableSetupAttempts + 1);
    if (setupExpandableInput()) {
        console.log('✅ Expandable input setup successful');
        return;
    }
    
    expandableSetupAttempts++;
    if (expandableSetupAttempts < maxExpandableAttempts) {
        const delay = 500 * Math.pow(2, expandableSetupAttempts - 1); // 500ms, 1000ms, 2000ms
        console.log(`❌ Expandable input not ready, retrying in ${delay}ms... (attempt ${expandableSetupAttempts}/${maxExpandableAttempts})`);
        setTimeout(trySetupExpandableInput, delay);
    } else {
        console.log('❌ Expandable input setup failed after all attempts');
    }
}

// Initial attempt after a short delay
setTimeout(trySetupExpandableInput, 500);

// Also use MutationObserver as backup
const expandableObserver = new MutationObserver((mutations) => {
    if (setupExpandableInput()) {
        expandableObserver.disconnect();
    }
});

expandableObserver.observe(document.body, {
    childList: true,
    subtree: true
});

// Removed watchExpandableState to prevent potential infinite loops

// Function to remove resource from start tab
function removeStartResource(index) {
    // Find the current resources state and update it
    const event = new CustomEvent('remove-start-resource', { detail: { index: index } });
    document.dispatchEvent(event);
}

// Listen for remove resource events and handle them
document.addEventListener('DOMContentLoaded', function() {
    // Set up listener for resource removal
    document.addEventListener('remove-start-resource', function(e) {
        const index = e.detail.index;
        // Trigger a click on the hidden remove buttons that Gradio creates
        const removeButtons = document.querySelectorAll('.start-resources-list button');
        if (removeButtons[index]) {
            // Find the corresponding Gradio button and click it
            const gradioButtons = document.querySelectorAll('[id*="component-"][id*="button"]');
            gradioButtons.forEach(btn => {
                if (btn.textContent === 'Remove' && btn.offsetParent) {
                    btn.click();
                }
            });
        }
    });
});

// Tab switching helper
function switchToDraftTab() {
    console.log('Switching to Update + Generate tab');

    // Find all tab buttons
    const tabButtons = document.querySelectorAll('button[role="tab"]');
    console.log('DEBUG: Found tab buttons:', tabButtons.length);
    
    // Log all tab button texts for debugging
    tabButtons.forEach((button, index) => {
        console.log(`DEBUG: Tab ${index}: "${button.textContent.trim()}"`);
    });

    // Find the Update + Generate tab button and click it (the second tab)
    let found = false;
    tabButtons.forEach(button => {
        if (button.textContent.includes('Update + Generate')) {
            console.log('DEBUG: Found Update + Generate tab, clicking...');
            button.click();
            console.log('Clicked Update + Generate tab');
            found = true;
        }
    });
    
    if (!found) {
        console.log('DEBUG: No Update + Generate tab found');
    }
}

// Track processed trigger timestamps to prevent repeated switching
let processedTriggers = new Set();

// Check for switch signal in a hidden element
setInterval(() => {
    const switchTrigger = document.getElementById('switch-tab-trigger');
    if (switchTrigger) {
        const currentContent = switchTrigger.innerHTML;
        
        if (currentContent && currentContent.includes('SWITCH_TO_DRAFT_TAB')) {
            // Extract timestamp from the trigger
            const match = currentContent.match(/SWITCH_TO_DRAFT_TAB_(\d+)/);
            if (match) {
                const timestamp = match[1];
                
                // Only process if we haven't seen this timestamp before
                if (!processedTriggers.has(timestamp)) {
                    console.log('DEBUG: Found new SWITCH_TO_DRAFT_TAB trigger with timestamp:', timestamp);
                    processedTriggers.add(timestamp);
                    switchToDraftTab();
                    
                    // Clean up old timestamps (keep only last 10)
                    if (processedTriggers.size > 10) {
                        const timestamps = Array.from(processedTriggers).sort();
                        processedTriggers.delete(timestamps[0]);
                    }
                } else {
                    console.log('DEBUG: Ignoring already processed trigger:', timestamp);
                }
            }
        }
    }
}, 100);

// Re-initialize expandable functionality when returning to Start tab
document.addEventListener('click', function(e) {
    // Only show detailed logging for tab clicks to reduce noise
    if (e.target && e.target.getAttribute('role') === 'tab') {
        console.log('DEBUG: Tab click detected on element:', e.target);
        console.log('DEBUG: Element role:', e.target.getAttribute('role'));
        console.log('DEBUG: Element textContent:', e.target.textContent);
        console.log('DEBUG: Element classList:', e.target.classList);
        
        // Try multiple ways to detect Draft tab click (it's called "Draft" not "Start")
        const isDraftTab1 = e.target && e.target.getAttribute('role') === 'tab' && e.target.textContent.includes('Draft');
        const isDraftTab2 = e.target && e.target.textContent && e.target.textContent.trim() === 'Draft';
        const isDraftTab3 = e.target && e.target.classList && e.target.classList.contains('tab') && e.target.textContent.includes('Draft');
        const isDraftTab4 = e.target && e.target.closest('button[role="tab"]') && e.target.textContent.includes('Draft');
        
        console.log('DEBUG: Draft tab detection methods:');
        console.log('  Method 1 (role=tab + Draft text):', isDraftTab1);
        console.log('  Method 2 (text === Draft):', isDraftTab2);  
        console.log('  Method 3 (class=tab + Draft text):', isDraftTab3);
        console.log('  Method 4 (closest tab + Draft text):', isDraftTab4);
        
        if (isDraftTab1 || isDraftTab2 || isDraftTab3 || isDraftTab4) {
            console.log('🔄 DEBUG: Draft tab clicked, re-initializing expandable functionality');
            setTimeout(() => {
                // Reset the setup attempts counter to allow re-setup
                expandableSetupAttempts = 0;
                console.log('🔄 DEBUG: About to call trySetupExpandableInput()');
                trySetupExpandableInput();
            }, 100);
        }
    }
});

// Also try using MutationObserver to detect when Start tab becomes visible
const tabObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'aria-selected') {
            const target = mutation.target;
            if (target.textContent && target.textContent.includes('Draft') && target.getAttribute('aria-selected') === 'true') {
                console.log('DEBUG: Draft tab became active via MutationObserver');
                setTimeout(() => {
                    expandableSetupAttempts = 0;
                    trySetupExpandableInput();
                }, 100);
            }
        }
    });
});

// Start observing tab changes
setTimeout(() => {
    const tabContainer = document.querySelector('.tab-nav') || document.querySelector('[role="tablist"]');
    if (tabContainer) {
        console.log('DEBUG: Found tab container, starting MutationObserver');
        tabObserver.observe(tabContainer, {
            attributes: true,
            subtree: true,
            attributeFilter: ['aria-selected']
        });
    } else {
        console.log('DEBUG: No tab container found for MutationObserver');
    }
}, 1000);

// Note: Resource icons now handled by CSS based on tab structure

// Note: Resource delete buttons now use onclick attribute directly

// Delete resource function
function deleteResource(resourcePath) {
    console.log('deleteResource called with resourcePath:', resourcePath);
    // Set the resource path in the hidden textbox
    const resourcePathInput = document.getElementById('delete-resource-path');
    console.log('Delete resource path input element:', resourcePathInput);

    if (resourcePathInput) {
        // Find the textarea element and set its value
        const textarea = resourcePathInput.querySelector('textarea') || resourcePathInput.querySelector('input[type="text"]');
        console.log('Delete resource textarea element:', textarea);

        if (textarea) {
            textarea.value = resourcePath;
            textarea.dispatchEvent(new Event('input', { bubbles: true }));

            // Trigger the hidden delete button
            const deleteButton = document.getElementById('delete-resource-trigger');
            console.log('Delete resource trigger button:', deleteButton);

            if (deleteButton) {
                deleteButton.click();
                console.log('Clicked delete resource trigger');
            } else {
                console.error('Delete resource trigger button not found');
            }
        } else {
            console.error('Delete resource textarea not found');
        }
    } else {
        console.error('Delete resource path input not found');
    }
}

// Delete block function
function deleteBlock(blockId) {
    console.log('deleteBlock called with blockId:', blockId);
    // Set the block ID in the hidden textbox
    const blockIdInput = document.getElementById('delete-block-id');
    console.log('Delete block ID input element:', blockIdInput);

    if (blockIdInput) {
        // Find the textarea element and set its value
        const textarea = blockIdInput.querySelector('textarea') || blockIdInput.querySelector('input[type="text"]');
        console.log('Delete block textarea element:', textarea);

        if (textarea) {
            textarea.value = blockId;
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('Set block ID in textarea:', blockId);

            // Trigger the hidden delete button
            setTimeout(() => {
                const deleteBtn = document.getElementById('delete-trigger');
                console.log('Delete trigger button:', deleteBtn);

                if (deleteBtn) {
                    deleteBtn.click();
                    console.log('Clicked delete trigger button');
                } else {
                    console.error('Delete trigger button not found!');
                }
            }, 100);
        } else {
            console.error('Textarea not found in delete block ID input!');
        }
    } else {
        console.error('Delete block ID input not found!');
    }
}

// Update block content function
function updateBlockContent(blockId, content) {
    console.log('updateBlockContent called with blockId:', blockId, 'content:', content);
    // Set the block ID and content in hidden inputs
    const blockIdInput = document.getElementById('update-block-id');
    const contentInput = document.getElementById('update-content-input');
    console.log('Update block ID input:', blockIdInput, 'Content input:', contentInput);

    if (blockIdInput && contentInput) {
        const blockIdTextarea = blockIdInput.querySelector('textarea') || blockIdInput.querySelector('input[type="text"]');
        const contentTextarea = contentInput.querySelector('textarea') || contentInput.querySelector('input[type="text"]');
        console.log('Block ID textarea:', blockIdTextarea, 'Content textarea:', contentTextarea);

        if (blockIdTextarea && contentTextarea) {
            blockIdTextarea.value = blockId;
            contentTextarea.value = content;
            console.log('Set values in textareas');

            // Dispatch input events
            blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            contentTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('Dispatched input events');

            // Trigger the update button
            setTimeout(() => {
                const updateBtn = document.getElementById('update-trigger');
                console.log('Update trigger button:', updateBtn);

                if (updateBtn) {
                    updateBtn.click();
                    console.log('Clicked update trigger button');
                } else {
                    console.error('Update trigger button not found!');
                }
            }, 100);
        } else {
            console.error('One or both textareas not found!');
        }
    } else {
        console.error('One or both input containers not found!');
    }
}

// Update block heading function
function updateBlockHeading(blockId, heading) {
    console.log('updateBlockHeading called with blockId:', blockId, 'heading:', heading);
    // Set the block ID and heading in hidden inputs
    const blockIdInput = document.getElementById('update-heading-block-id');
    const headingInput = document.getElementById('update-heading-input');
    console.log('Block ID input element:', blockIdInput);
    console.log('Heading input element:', headingInput);

    if (blockIdInput && headingInput) {
        const blockIdTextarea = blockIdInput.querySelector('textarea') || blockIdInput.querySelector('input[type="text"]');
        const headingTextarea = headingInput.querySelector('textarea') || headingInput.querySelector('input[type="text"]');
        console.log('Block ID textarea:', blockIdTextarea);
        console.log('Heading textarea:', headingTextarea);

        if (blockIdTextarea && headingTextarea) {
            blockIdTextarea.value = blockId;
            headingTextarea.value = heading;
            console.log('Set block ID:', blockId);
            console.log('Set heading:', heading);

            // Dispatch input events
            blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            headingTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('Dispatched input events for both textareas');

            // Trigger the update button
            setTimeout(() => {
                const updateBtn = document.getElementById('update-heading-trigger');
                console.log('Update heading trigger button:', updateBtn);

                if (updateBtn) {
                    updateBtn.click();
                    console.log('Clicked update heading trigger button');
                } else {
                    console.error('Update heading trigger button not found!');
                }
            }, 100);
        } else {
            console.error('One or both textareas not found!');
            console.error('blockIdTextarea:', blockIdTextarea);
            console.error('headingTextarea:', headingTextarea);
        }
    } else {
        console.error('One or both input containers not found!');
        console.error('blockIdInput:', blockIdInput);
        console.error('headingInput:', headingInput);
    }
}

// Toggle block collapse function
function toggleBlockCollapse(blockId) {
    console.log('toggleBlockCollapse called with blockId:', blockId);
    // Set the block ID in the hidden input
    const blockIdInput = document.getElementById('toggle-block-id');
    console.log('Toggle block ID input:', blockIdInput);

    if (blockIdInput) {
        const textarea = blockIdInput.querySelector('textarea') || blockIdInput.querySelector('input[type="text"]');
        console.log('Toggle block textarea:', textarea);

        if (textarea) {
            textarea.value = blockId;
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('Set block ID in textarea:', blockId);

            // Trigger the hidden toggle button
            setTimeout(() => {
                const toggleBtn = document.getElementById('toggle-trigger');
                console.log('Toggle trigger button:', toggleBtn);

                if (toggleBtn) {
                    toggleBtn.click();
                    console.log('Clicked toggle trigger button');
                } else {
                    console.error('Toggle trigger button not found!');
                }
            }, 100);
        } else {
            console.error('Textarea not found in toggle block ID input!');
        }
    } else {
        console.error('Toggle block ID input not found!');
    }
}

// Expand block if collapsed when heading is focused
function expandBlockOnHeadingFocus(blockId) {
    // Find the block element using data-id attribute
    const block = document.querySelector(`[data-id="${blockId}"]`);
    if (block && block.classList.contains('collapsed')) {
        // Store reference to the heading input and cursor position
        const headingInput = block.querySelector('.block-heading-inline');
        const cursorPosition = headingInput ? headingInput.selectionStart : 0;

        // If the block is collapsed, expand it
        toggleBlockCollapse(blockId);

        // Use a longer delay and multiple attempts to ensure focus is restored
        let attempts = 0;
        const maxAttempts = 5;

        const restoreFocus = () => {
            attempts++;
            const updatedBlock = document.querySelector(`[data-id="${blockId}"]`);
            const updatedHeading = updatedBlock ? updatedBlock.querySelector('.block-heading-inline') : null;

            if (updatedHeading && !updatedBlock.classList.contains('collapsed')) {
                // Block has expanded, restore focus
                updatedHeading.focus();
                // Restore cursor position
                updatedHeading.setSelectionRange(cursorPosition, cursorPosition);
            } else if (attempts < maxAttempts) {
                // Try again after a short delay
                setTimeout(restoreFocus, 100);
            }
        };

        // Start trying after initial delay
        setTimeout(restoreFocus, 200);
    }
}

// Auto-expand textarea function
function autoExpandTextarea(textarea) {
    // Skip document description - it's handled by setupDescriptionToggle
    const isDocDescription = textarea.closest('#doc-description-id');
    if (isDocDescription) {
        return;
    }

    // Handle resource description textareas specially
    const isResourceDesc = textarea.closest('.resource-desc-gradio');
    if (isResourceDesc) {
        autoExpandResourceDescription(textarea);
        return;
    }
    
    // Skip the main start prompt input - it should maintain its own sizing
    const isStartPromptInput = textarea.closest('#start-prompt-input');
    if (isStartPromptInput) {
        console.log('🚫 Skipping auto-expand for main start prompt input');
        return;
    }

    // For other textareas, use height-based method
    textarea.style.height = 'auto';
    const newHeight = textarea.scrollHeight + 2;
    textarea.style.height = newHeight + 'px';
    textarea.style.maxHeight = '';
    textarea.style.overflow = 'hidden';
    textarea.classList.remove('scrollable');
}

// Auto-expand function specifically for resource descriptions
function autoExpandResourceDescription(textarea) {
    if (!textarea) return;
    
    // Reset height to auto to get accurate scrollHeight
    const originalHeight = textarea.style.height;
    textarea.style.height = 'auto';
    
    // Calculate the needed height more accurately
    const scrollHeight = textarea.scrollHeight;
    const computedStyle = window.getComputedStyle(textarea);
    const lineHeight = parseFloat(computedStyle.lineHeight) || 15.4; // 11px * 1.4
    const paddingTop = parseFloat(computedStyle.paddingTop) || 4;
    const paddingBottom = parseFloat(computedStyle.paddingBottom) || 4;
    const borderTop = parseFloat(computedStyle.borderTopWidth) || 0;
    const borderBottom = parseFloat(computedStyle.borderBottomWidth) || 0;
    const totalVerticalPadding = paddingTop + paddingBottom + borderTop + borderBottom;
    
    // Calculate number of lines based on content height
    const contentHeight = scrollHeight - totalVerticalPadding;
    const lines = Math.max(1, Math.round(contentHeight / lineHeight));
    
    // Set minimum of 2 lines, maximum of 8 lines
    const minLines = 2;
    const maxLines = 8;
    const finalLines = Math.max(minLines, Math.min(maxLines, lines));
    
    // Calculate final height
    const finalHeight = (finalLines * lineHeight) + totalVerticalPadding;
    
    // Apply the height with !important to override any CSS
    textarea.style.setProperty('height', finalHeight + 'px', 'important');
    
    // Handle scrolling if content exceeds max lines
    if (lines > maxLines) {
        textarea.style.setProperty('overflow-y', 'auto', 'important');
        textarea.classList.add('scrollable');
    } else {
        textarea.style.setProperty('overflow-y', 'hidden', 'important');
        textarea.classList.remove('scrollable');
    }
    
    console.log(`🔧 Resource desc auto-expand - content: "${textarea.value.substring(0, 50)}...", lines: ${lines}, finalLines: ${finalLines}, height: ${finalHeight}px`);
    
    // Debug: Check if the height was actually applied
    setTimeout(() => {
        const actualHeight = window.getComputedStyle(textarea).height;
        const actualScrollHeight = textarea.scrollHeight;
        console.log(`🔧 Height check - set: ${finalHeight}px, actual: ${actualHeight}, scrollHeight: ${actualScrollHeight}px`);
        
        // Only override if there's a significant difference (more than 1px)
        if (Math.abs(parseFloat(actualHeight) - finalHeight) > 1) {
            console.log('🔧 Significant height override detected, forcing with inline style');
            textarea.setAttribute('style', `height: ${finalHeight}px !important; overflow-y: ${lines > maxLines ? 'auto' : 'hidden'} !important;`);
        } else {
            console.log('🔧 Height applied correctly (within tolerance)');
        }
    }, 100);
}

// Setup auto-expand for all textareas
function setupAutoExpand() {
    // Get all textareas in the document
    const textareas = document.querySelectorAll('textarea');

    textareas.forEach(textarea => {
        // Always setup/re-setup to handle re-renders

        // Initial sizing
        autoExpandTextarea(textarea);

        // Remove existing listeners by using a named function
        if (!textarea.autoExpandHandler) {
            textarea.autoExpandHandler = function() {
                autoExpandTextarea(this);
            };
            textarea.pasteHandler = function() {
                setTimeout(() => autoExpandTextarea(this), 10);
            };

            // Add event listeners
            textarea.addEventListener('input', textarea.autoExpandHandler);
            textarea.addEventListener('paste', textarea.pasteHandler);
        }
    });

    // Special handling for the document description to ensure proper initial height
    const docDescription = document.querySelector('#doc-description-id textarea');
    if (docDescription) {
        // Remove the watcher - it's causing issues
        // The setupDescriptionToggle handles everything needed
    }
}

// Try setting up when DOM loads and with a delay
document.addEventListener('DOMContentLoaded', function () {
    refresh();
    // Upload resource setup no longer needed - using Gradio's native component
    setupAutoExpand();
});

// Reset document description on new document
function resetDocumentDescription() {
    const docDescriptionBox = document.querySelector('.doc-description-box');
    const docDescriptionTextarea = document.querySelector('#doc-description-id textarea');

    if (docDescriptionBox && docDescriptionTextarea) {
        // Clear the textarea value
        docDescriptionTextarea.value = '';


        // Ensure the box is collapsed
        if (!docDescriptionBox.classList.contains('collapsed')) {
            docDescriptionBox.classList.add('collapsed');
        }

        // Reset the textarea height
        docDescriptionTextarea.style.height = 'auto';
        autoExpandTextarea(docDescriptionTextarea);

        // Hide the expand button
        const expandBtn = docDescriptionBox.querySelector('.desc-expand-btn');
        if (expandBtn) {
            expandBtn.style.display = 'none';
        }
    }
}

// Track if we're dragging from an external source
let isDraggingFromExternal = false;

// Clear draggedResource when dragging files from outside the browser
document.addEventListener('dragenter', function(e) {
    // Only clear draggedResource if we don't already have one AND this looks like an external drag
    if (!draggedResource && e.dataTransfer && e.dataTransfer.types) {
        // Check if this is likely an external file drag
        const hasFiles = e.dataTransfer.types.includes('Files') ||
                        e.dataTransfer.types.includes('application/x-moz-file');

        // Also check that it's not coming from our resource items
        const isFromResourceItem = e.target.closest('.resource-item');

        if (hasFiles && !isFromResourceItem && !isDraggingFromExternal) {
            isDraggingFromExternal = true;
            console.log('External file drag detected');
            draggedResource = null;
        }
    }
}, true); // Use capture phase to run before other handlers

// Reset the external drag flag when drag ends
document.addEventListener('dragleave', function(e) {
    // Check if we're leaving the document entirely
    if (e.clientX === 0 && e.clientY === 0) {
        isDraggingFromExternal = false;
    }
});

document.addEventListener('drop', function(e) {
    isDraggingFromExternal = false;
});

// Also reset when starting to drag a resource
document.addEventListener('dragstart', function(e) {
    if (e.target.closest('.resource-item')) {
        isDraggingFromExternal = false;
    }
});

// Setup observers for resource title changes in Gradio components
function setupResourceTitleObservers() {
    const resourceItems = document.querySelectorAll('.resource-item-gradio');
    console.log('Setting up title observers for', resourceItems.length, 'resource items');

    resourceItems.forEach((item, index) => {
        // Find the title textarea
        const titleTextarea = item.querySelector('.resource-title-gradio input');
        const pathDiv = item.querySelector('.resource-path-hidden');

        if (titleTextarea && pathDiv) {
            const resourcePath = pathDiv.getAttribute('data-path') || pathDiv.textContent.trim();
            console.log(`Resource ${index}: path="${resourcePath}"`);

            // Remove any existing listener to avoid duplicates
            titleTextarea.removeEventListener('input', titleTextarea._titleUpdateHandler);

            // Create and store the handler function
            titleTextarea._titleUpdateHandler = function() {
                const newTitle = this.value;
                console.log(`Title changed for resource "${resourcePath}": "${newTitle}"`);

                // Immediately update all dropped resources with this path
                const droppedResources = document.querySelectorAll('.dropped-resource[data-resource-path]');
                console.log(`Found ${droppedResources.length} dropped resources to check`);

                droppedResources.forEach(dropped => {
                    const droppedPath = dropped.getAttribute('data-resource-path');
                    console.log(`Checking dropped resource with path="${droppedPath}"`);

                    if (droppedPath === resourcePath) {
                        const titleSpan = dropped.querySelector('.dropped-resource-title');
                        if (titleSpan) {
                            console.log(`Updating title span to: "${newTitle}"`);
                            titleSpan.textContent = newTitle;
                        }
                    }
                });
            };

            // Add the event listener
            titleTextarea.addEventListener('input', titleTextarea._titleUpdateHandler);
            console.log(`Added input listener to resource ${index}`);
        } else {
            console.log(`Resource ${index}: Missing textarea or path div`);
        }
    });
}

window.addEventListener('load', function() {
    console.log('Window load event fired');
    // Upload resource setup no longer needed - using Gradio's native component
    setTimeout(setupAutoExpand, 100);
    // Also setup drag and drop on window load
    setTimeout(setupDragAndDrop, 200);
    setTimeout(setupFileUploadDragAndDrop, 250);
    // Removed setupDescriptionToggle - causes phantom Gradio events

    // Set up a global observer for the resources column
    setupResourceObserver();

    // Setup title observers for dynamic updates
    setTimeout(() => {
        console.log('About to call setupResourceTitleObservers');
        const resourceItems = document.querySelectorAll('.resource-item-gradio');
        console.log('Found', resourceItems.length, 'resource items before calling setup');
        setupResourceTitleObservers();
    }, 300);
});

// Function to set up observer for resources
function setupResourceObserver() {
    let resourceSetupTimeout;

    // Function to observe a resources area
    function observeResourcesArea(resourcesArea) {
        if (!resourcesArea) return;

        const resourceObserver = new MutationObserver((mutations) => {
            // Clear any pending timeout
            clearTimeout(resourceSetupTimeout);

            // Check if resource items were added
            let hasResourceChanges = false;
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1 &&
                        (node.classList?.contains('resource-item') ||
                         node.querySelector?.('.resource-item'))) {
                        hasResourceChanges = true;
                    }
                });
            });

            if (hasResourceChanges) {
                console.log('Resources added, setting up drag and drop');
                // Wait a bit for DOM to stabilize then setup drag and drop
                resourceSetupTimeout = setTimeout(() => {
                    setupDragAndDrop();
                    setupResourceTitleObservers();
                }, 200);
            }
        });

        resourceObserver.observe(resourcesArea, {
            childList: true,
            subtree: true
        });

        return resourceObserver;
    }

    // Initial setup
    let currentObserver = observeResourcesArea(document.querySelector('.resources-display-area'));

    // Also watch for the resources area itself being replaced
    const columnObserver = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1) {
                    const newResourcesArea = node.classList?.contains('resources-display-area') ?
                        node : node.querySelector?.('.resources-display-area');

                    if (newResourcesArea) {
                        console.log('Resources area replaced, setting up new observer');
                        // Disconnect old observer if it exists
                        if (currentObserver) {
                            currentObserver.disconnect();
                        }
                        // Set up new observer
                        currentObserver = observeResourcesArea(newResourcesArea);
                        // Setup drag and drop for any existing items
                        setTimeout(setupDragAndDrop, 200);
                        // Setup title observers too
                        setTimeout(setupResourceTitleObservers, 300);
                    }
                }
            });
        });
    });

    // Observe the resources column for replacements
    const resourcesCol = document.querySelector('.resources-col');
    if (resourcesCol) {
        columnObserver.observe(resourcesCol, {
            childList: true,
            subtree: true
        });
    }
}

// Prevent dropping resources on text inputs and file upload zones
function preventInvalidDrops() {
    // Helper function to check if element is invalid drop target
    function isInvalidDropTarget(element) {
        if (!element) return false;

        // Check if it's a text input
        if (element.tagName === 'TEXTAREA' || element.tagName === 'INPUT') {
            return true;
        }

        // Check if it's part of a file upload component (Gradio file upload)
        if (element.closest('.resource-upload-gradio') ||
            element.closest('[data-testid="file"]') ||
            element.classList.contains('resource-upload-gradio')) {
            return true;
        }

        return false;
    }

    // Prevent drop on invalid targets
    document.addEventListener('dragover', function(e) {
        if (isInvalidDropTarget(e.target)) {
            if (draggedResource || window.currentDraggedResource) {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'none';
                e.target.classList.add('no-drop');
            }
        }
    }, true);

    document.addEventListener('dragleave', function(e) {
        if (isInvalidDropTarget(e.target)) {
            e.target.classList.remove('no-drop');
        }
    }, true);

    document.addEventListener('drop', function(e) {
        if (isInvalidDropTarget(e.target)) {
            if (draggedResource || window.currentDraggedResource) {
                e.preventDefault();
                e.stopPropagation();
                e.target.classList.remove('no-drop');
                console.log('Prevented drop on invalid target:', e.target);
            }
        }
    }, true);

    // Clean up no-drop class when drag ends
    document.addEventListener('dragend', function(e) {
        document.querySelectorAll('.no-drop').forEach(el => {
            el.classList.remove('no-drop');
        });
    }, true);
}

// Call it once when the page loads
preventInvalidDrops();

// Use MutationObserver for dynamic content
let debounceTimer;
const observer = new MutationObserver(function(mutations) {
    // Check if any mutations are relevant (new nodes added)
    let hasRelevantChanges = false;

    for (const mutation of mutations) {
        // Only care about added nodes
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            // Check if any added nodes contain textareas or are blocks
            for (const node of mutation.addedNodes) {
                if (node.nodeType === 1) { // Element node
                    if (node.classList?.contains('content-block') ||
                        node.classList?.contains('resource-item') ||
                        node.classList?.contains('resource-item-gradio') ||
                        node.classList?.contains('block-resources') ||
                        node.querySelector?.('textarea') ||
                        node.querySelector?.('.resource-item') ||
                        node.querySelector?.('.resource-item-gradio') ||
                        node.querySelector?.('.block-resources') ||
                        node.tagName === 'TEXTAREA') {
                        hasRelevantChanges = true;
                        // Log when we detect resource items
                        if (node.classList?.contains('resource-item') ||
                            node.classList?.contains('resource-item-gradio') ||
                            node.querySelector?.('.resource-item') ||
                            node.querySelector?.('.resource-item-gradio')) {
                            console.log('Detected resource item change');
                        }
                        break;
                    }
                }
            }
        }
    }

    // Only run setup if relevant changes detected
    if (hasRelevantChanges) {
        refresh();
        // Upload resource setup no longer needed - using Gradio's native component
        setupImportButton();

        // Delay drag and drop setup slightly to ensure DOM is ready
        setTimeout(() => {
            setupDragAndDrop();
            setupFileUploadDragAndDrop();
            setupResourceTitleObservers();
        }, 50);

        // Debounce the setupAutoExpand to avoid multiple calls
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            setupAutoExpand();
            // Removed setupDescriptionToggle() - causes phantom Gradio events
            setupExampleSelection();
            // Removed setupResourceDescriptions() - causes phantom Gradio events
            setupResourceUploadZones();
            setupResourceUploadText();
            preventResourceDrops();
        }, 100);
    }
});

if (document.body) {
    observer.observe(document.body, {
        childList: true,
        subtree: true
        // Removed attributes observation - we don't need it
    });
}

// Update block indent function
function updateBlockIndent(blockId, direction) {
    console.log('updateBlockIndent called with blockId:', blockId, 'direction:', direction);

    // Set focused block when indenting
    setFocusedBlock(blockId);
    console.log('Called setFocusedBlock for blockId:', blockId);

    // Set the block ID and direction in hidden inputs
    const blockIdInput = document.getElementById('indent-block-id');
    const directionInput = document.getElementById('indent-direction');
    console.log('Block ID input element:', blockIdInput);
    console.log('Direction input element:', directionInput);

    if (blockIdInput && directionInput) {
        const blockIdTextarea = blockIdInput.querySelector('textarea') || blockIdInput.querySelector('input[type="text"]');
        const directionTextarea = directionInput.querySelector('textarea') || directionInput.querySelector('input[type="text"]');
        console.log('Block ID textarea:', blockIdTextarea);
        console.log('Direction textarea:', directionTextarea);

        if (blockIdTextarea && directionTextarea) {
            blockIdTextarea.value = blockId;
            directionTextarea.value = direction;
            console.log('Set block ID:', blockId);
            console.log('Set direction:', direction);

            // Dispatch input events
            blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            directionTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('Dispatched input events for both textareas');

            // Trigger the update button
            setTimeout(() => {
                const indentBtn = document.getElementById('indent-trigger');
                console.log('Indent trigger button:', indentBtn);

                if (indentBtn) {
                    indentBtn.click();
                    console.log('Clicked indent trigger button');
                } else {
                    console.error('Indent trigger button not found!');
                }
            }, 100);
        } else {
            console.error('One or both textareas not found!');
            console.error('blockIdTextarea:', blockIdTextarea);
            console.error('directionTextarea:', directionTextarea);
        }
    } else {
        console.error('One or both input containers not found!');
        console.error('blockIdInput:', blockIdInput);
        console.error('directionInput:', directionInput);
    }
}

// Set focused block function
function setFocusedBlock(blockId, skipRender = false) {
    console.log('setFocusedBlock called with blockId:', blockId, 'skipRender:', skipRender);

    const focusIdInput = document.getElementById('focus-block-id');
    console.log('Focus ID input element:', focusIdInput);

    if (focusIdInput) {
        const textarea = focusIdInput.querySelector('textarea') || focusIdInput.querySelector('input[type="text"]');
        console.log('Focus ID textarea:', textarea);

        if (textarea) {
            textarea.value = blockId;
            console.log('Set focus block ID:', blockId);

            textarea.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('Dispatched input event');

            // Only trigger render if not skipping
            if (!skipRender) {
                console.log('Not skipping render, will trigger focus button');
                setTimeout(() => {
                    const focusBtn = document.getElementById('focus-trigger');
                    console.log('Focus trigger button:', focusBtn);

                    if (focusBtn) {
                        focusBtn.click();
                        console.log('Clicked focus trigger button');
                    } else {
                        console.error('Focus trigger button not found!');
                    }
                }, 100);
            } else {
                console.log('Skipping render as requested');
            }
        } else {
            console.error('Textarea not found in focus ID input!');
        }
    } else {
        console.error('Focus ID input not found!');
    }
}


// Add block after function - adds same type as the block being clicked
function addBlockAfter(blockId) {
    // Get the block element to determine its type
    const blockElement = document.querySelector(`[data-id="${blockId}"]`);
    if (blockElement) {
        // Determine type based on class
        let blockType = 'ai'; // default
        if (blockElement.classList.contains('text-block')) {
            blockType = 'text';
        }

        // Set the values in hidden inputs
        const blockIdInput = document.getElementById('add-after-block-id');
        const typeInput = document.getElementById('add-after-type');

        if (blockIdInput && typeInput) {
            const blockIdTextarea = blockIdInput.querySelector('textarea') || blockIdInput.querySelector('input[type="text"]');
            const typeTextarea = typeInput.querySelector('textarea') || typeInput.querySelector('input[type="text"]');

            if (blockIdTextarea && typeTextarea) {
                blockIdTextarea.value = blockId;
                typeTextarea.value = blockType;

                // Dispatch input events
                blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
                typeTextarea.dispatchEvent(new Event('input', { bubbles: true }));

                // Trigger the add after button
                setTimeout(() => {
                    const addAfterBtn = document.getElementById('add-after-trigger');
                    if (addAfterBtn) {
                        addAfterBtn.click();
                    }
                }, 100);
            }
        }
    }
}

// Convert block type function
function convertBlock(blockId, toType) {
    console.log('convertBlock called with blockId:', blockId, 'toType:', toType);

    // Set the values in hidden inputs
    const blockIdInput = document.getElementById('convert-block-id');
    const typeInput = document.getElementById('convert-type');
    console.log('Block ID input element:', blockIdInput);
    console.log('Type input element:', typeInput);

    if (blockIdInput && typeInput) {
        const blockIdTextarea = blockIdInput.querySelector('textarea') || blockIdInput.querySelector('input[type="text"]');
        const typeTextarea = typeInput.querySelector('textarea') || typeInput.querySelector('input[type="text"]');
        console.log('Block ID textarea:', blockIdTextarea);
        console.log('Type textarea:', typeTextarea);

        if (blockIdTextarea && typeTextarea) {
            blockIdTextarea.value = blockId;
            typeTextarea.value = toType;
            console.log('Set block ID:', blockId);
            console.log('Set convert to type:', toType);

            // Dispatch input events
            blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            typeTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('Dispatched input events for both textareas');

            // Trigger the convert button
            setTimeout(() => {
                const convertBtn = document.getElementById('convert-trigger');
                console.log('Convert trigger button:', convertBtn);

                if (convertBtn) {
                    convertBtn.click();
                    console.log('Clicked convert trigger button');

                    // Focus the textarea after conversion
                    setTimeout(() => {
                        const block = document.querySelector(`[data-id="${blockId}"]`);
                        console.log('Found converted block:', block);

                        if (block) {
                            const textarea = block.querySelector('textarea') || block.querySelector('input[type="text"]');
                            console.log('Found textarea in converted block:', textarea);

                            if (textarea) {
                                textarea.focus();
                                console.log('Focused textarea in converted block');
                            }
                        }
                    }, 200);
                } else {
                    console.error('Convert trigger button not found!');
                }
            }, 100);
        } else {
            console.error('One or both textareas not found!');
            console.error('blockIdTextarea:', blockIdTextarea);
            console.error('typeTextarea:', typeTextarea);
        }
    } else {
        console.error('One or both input containers not found!');
        console.error('blockIdInput:', blockIdInput);
        console.error('typeInput:', typeInput);
    }
}

// Focus textarea within a block
function focusBlockTextarea(blockId) {
    const block = document.querySelector(`[data-id="${blockId}"]`);
    if (block) {
        const textarea = block.querySelector('textarea') || block.querySelector('input[type="text"]');
        if (textarea) {
            textarea.focus();
        }
    }
}

// Delete resource from panel function
function deleteResourceFromPanel(resourcePath) {
    // Set the value in hidden input
    const resourcePathInput = document.getElementById('delete-panel-resource-path');

    if (resourcePathInput) {
        const resourcePathTextarea = resourcePathInput.querySelector('textarea') || resourcePathInput.querySelector('input[type="text"]');

        if (resourcePathTextarea) {
            resourcePathTextarea.value = resourcePath;

            // Dispatch input event
            resourcePathTextarea.dispatchEvent(new Event('input', { bubbles: true }));

            // Trigger the delete button
            setTimeout(() => {
                const deleteBtn = document.getElementById('delete-panel-resource-trigger');
                if (deleteBtn) {
                    deleteBtn.click();
                }
            }, 100);
        }
    }
}

// Remove resource from block function
function removeBlockResource(blockId, resourcePath) {
    console.log('removeBlockResource called with blockId:', blockId, 'resourcePath:', resourcePath);
    // Set the values in hidden inputs
    const blockIdInput = document.getElementById('remove-resource-block-id');
    const resourcePathInput = document.getElementById('remove-resource-path');
    console.log('Block ID input:', blockIdInput, 'Resource path input:', resourcePathInput);

    if (blockIdInput && resourcePathInput) {
        const blockIdTextarea = blockIdInput.querySelector('textarea') || blockIdInput.querySelector('input[type="text"]');
        const resourcePathTextarea = resourcePathInput.querySelector('textarea') || resourcePathInput.querySelector('input[type="text"]');
        console.log('Block ID textarea:', blockIdTextarea, 'Resource path textarea:', resourcePathTextarea);

        if (blockIdTextarea && resourcePathTextarea) {
            blockIdTextarea.value = blockId;
            resourcePathTextarea.value = resourcePath;
            console.log('Set values in textareas');

            // Dispatch input events
            blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            resourcePathTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('Dispatched input events');

            // Trigger the remove button
            setTimeout(() => {
                const removeBtn = document.getElementById('remove-resource-trigger');
                console.log('Remove resource trigger button:', removeBtn);

                if (removeBtn) {
                    removeBtn.click();
                    console.log('Clicked remove resource trigger button');
                } else {
                    console.error('Remove resource trigger button not found!');
                }
            }, 100);
        } else {
            console.error('One or both textareas not found!');
        }
    } else {
        console.error('One or both input containers not found!');
    }
}

// Debounce timer for resource descriptions
let descriptionDebounceTimers = {};

// Update resource description function with debouncing
function updateResourceDescription(blockId, resourcePath, description) {
    // Create unique key for this input
    const timerKey = `${blockId}-${resourcePath}`;

    // Clear existing timer for this input
    if (descriptionDebounceTimers[timerKey]) {
        clearTimeout(descriptionDebounceTimers[timerKey]);
    }

    // Update all other description text boxes for the same resource immediately
    const allDescInputs = document.querySelectorAll('.resource-description');
    allDescInputs.forEach(input => {
        // Check if this input is for the same resource but different block
        if (input.getAttribute('oninput') &&
            input.getAttribute('oninput').includes(`'${resourcePath}'`) &&
            !input.getAttribute('oninput').includes(`'${blockId}'`)) {
            input.value = description;
        }
    });

    // Set new timer with 50ms delay (0.05 seconds after user stops typing)
    descriptionDebounceTimers[timerKey] = setTimeout(() => {
        // Set the values in hidden inputs
        const blockIdInput = document.getElementById('update-desc-block-id');
        const resourcePathInput = document.getElementById('update-desc-resource-path');
        const descTextInput = document.getElementById('update-desc-text');

        if (blockIdInput && resourcePathInput && descTextInput) {
            const blockIdTextarea = blockIdInput.querySelector('textarea') || blockIdInput.querySelector('input[type="text"]');
            const resourcePathTextarea = resourcePathInput.querySelector('textarea') || resourcePathInput.querySelector('input[type="text"]');
            const descTextTextarea = descTextInput.querySelector('textarea') || descTextInput.querySelector('input[type="text"]');

            if (blockIdTextarea && resourcePathTextarea && descTextTextarea) {
                blockIdTextarea.value = blockId;
                resourcePathTextarea.value = resourcePath;
                descTextTextarea.value = description;

                // Dispatch input events
                blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
                resourcePathTextarea.dispatchEvent(new Event('input', { bubbles: true }));
                descTextTextarea.dispatchEvent(new Event('input', { bubbles: true }));

                // Trigger the update button
                setTimeout(() => {
                    const updateBtn = document.getElementById('update-desc-trigger');
                    if (updateBtn) {
                        updateBtn.click();
                    }
                }, 100);
            }
        }

        // Clean up timer reference
        delete descriptionDebounceTimers[timerKey];
    }, 50); // Wait 50ms after user stops typing
}

// Load resource content into text block
function loadResourceContent(blockId, resourcePath) {
    // Set the values in hidden inputs
    const blockIdInput = document.getElementById('load-resource-block-id');
    const resourcePathInput = document.getElementById('load-resource-path');

    if (blockIdInput && resourcePathInput) {
        const blockIdTextarea = blockIdInput.querySelector('textarea') || blockIdInput.querySelector('input[type="text"]');
        const resourcePathTextarea = resourcePathInput.querySelector('textarea') || resourcePathInput.querySelector('input[type="text"]');

        if (blockIdTextarea && resourcePathTextarea) {
            blockIdTextarea.value = blockId;
            resourcePathTextarea.value = resourcePath;

            // Dispatch input events
            blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            resourcePathTextarea.dispatchEvent(new Event('input', { bubbles: true }));

            // Trigger the load button
            setTimeout(() => {
                const loadBtn = document.getElementById('load-resource-trigger');
                if (loadBtn) {
                    loadBtn.click();
                }
            }, 100);
        }
    }
}

// Setup description expand/collapse button
function setupDescriptionToggle() {
    const container = document.querySelector('#doc-description-id');
    const textarea = container?.querySelector('textarea') || container?.querySelector('input[type="text"]');

    if (!container || !textarea || container.dataset.toggleSetup) {
        return;
    }

    // Mark as setup
    container.dataset.toggleSetup = 'true';

    // Create expand/collapse button
    const button = document.createElement('button');
    button.className = 'desc-expand-btn';
    button.innerHTML = '⌵'; // Down chevron
    button.title = 'Collapse';

    // Find the input container (parent of textarea) and insert button there
    const inputContainer = textarea.parentElement;
    if (inputContainer) {
        inputContainer.style.position = 'relative'; // Ensure container is positioned
        inputContainer.appendChild(button);
    }

    // Track collapsed state and full text
    let isCollapsed = false;
    let fullText = '';

    // Function to get first two lines of text
    function getFirstTwoLines(text) {
        const lines = text.split('\n');
        // Take first two lines
        let firstTwo = lines.slice(0, 2).join('\n');

        // If the second line exists and there's more content, add ellipsis
        if (lines.length > 2 || (lines.length === 2 && lines[1].length > 50)) {
            firstTwo += '...';
        }

        return firstTwo;
    }

    // Function to check if button should be visible
    function checkButtonVisibility() {
        if (isCollapsed) return;

        // Count actual lines in the textarea
        const lines = textarea.value.split('\n');
        let totalLines = lines.length; // Start with actual line breaks

        // Add wrapped lines - estimate ~80 chars per line for wider doc description
        lines.forEach((line, index) => {
            if (line.length > 80) {
                // Add extra lines for wrapping
                totalLines += Math.floor(line.length / 80);
            }
        });

        console.log('Doc desc - lines:', lines.length, 'totalLines:', totalLines);

        // Show button if content exceeds 2 lines
        if (totalLines > 2) {
            button.style.display = 'block';
        } else {
            button.style.display = 'none';
        }

        // Set rows attribute based on content, no max
        let rowsToShow = Math.max(2, totalLines);

        // Add 1 extra row if we have 3 or more rows for breathing room
        if (rowsToShow >= 3) {
            rowsToShow += 1;
        }

        console.log('Setting rows to:', rowsToShow);

        textarea.rows = rowsToShow;
        textarea.style.height = 'auto'; // Use auto instead of empty string
        textarea.style.minHeight = 'auto';
        textarea.style.maxHeight = 'none';
        textarea.style.overflow = 'hidden';

        // Never add scrollable class
        textarea.classList.remove('scrollable');
    }

    // Toggle collapse/expand
    function toggleCollapse() {
        const lineHeight = parseFloat(window.getComputedStyle(textarea).lineHeight);
        const padding = parseInt(window.getComputedStyle(textarea).paddingTop) +
                       parseInt(window.getComputedStyle(textarea).paddingBottom);
        const twoLinesHeight = (lineHeight * 2) + padding;

        if (isCollapsed) {
            // Expand - restore full text
            textarea.value = fullText;
            textarea.style.height = ''; // Clear height
            textarea.style.maxHeight = ''; // Remove max height
            textarea.style.overflow = 'hidden'; // No scrollbars
            container.classList.remove('collapsed');
            button.innerHTML = '⌵';
            button.title = 'Collapse';
            isCollapsed = false;
            textarea.classList.remove('scrollable'); // Remove scrollable class
            checkButtonVisibility(); // Use checkButtonVisibility like resources
            // Keep focus without moving cursor
            textarea.focus();

            // Trigger input event to update Gradio's state
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
        } else {
            // Collapse - save full text and show only first 2 lines
            fullText = textarea.value;
            textarea.value = getFirstTwoLines(fullText);
            textarea.rows = 2; // Force 2 rows
            textarea.style.height = ''; // Let rows control height
            textarea.style.maxHeight = ''; // Clear max height
            textarea.style.overflow = 'hidden';
            container.classList.add('collapsed');
            button.innerHTML = '⌵';  // Same chevron, will rotate with CSS
            button.title = 'Expand';
            isCollapsed = true;
            textarea.classList.remove('scrollable'); // Remove scrollable class when collapsed
            // Remove focus to prevent scrolling
            textarea.blur();
        }
    }

    // Button click handler
    button.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        toggleCollapse();
    });

    // Click on collapsed textarea to expand
    textarea.addEventListener('click', (e) => {
        if (isCollapsed) {
            // Get cursor position before expanding
            const cursorPos = textarea.selectionStart;
            toggleCollapse();
            // Restore cursor position after expanding
            setTimeout(() => {
                textarea.setSelectionRange(cursorPos, cursorPos);
            }, 0);
        }
    });

    // Check on input
    textarea.addEventListener('input', () => {
        // Only update if not collapsed (unless typing to expand)
        if (!isCollapsed) {
            checkButtonVisibility();
        } else if (textarea.value !== getFirstTwoLines(fullText)) {
            // If collapsed and user is typing (not just the truncated value), expand
            toggleCollapse();
        }
    });

    // Also handle paste
    textarea.addEventListener('paste', function() {
        setTimeout(() => {
            if (!isCollapsed) {
                checkButtonVisibility();
            }
        }, 10);
    });

    // Initial check
    checkButtonVisibility();
}

// Also add a global function that can be called
window.setupAutoExpand = setupAutoExpand;

// Setup import button functionality
function setupImportButton() {
    const importBtn = document.getElementById('import-builder-btn-id');
    console.log('Setting up import button, found:', importBtn);

    if (importBtn) {
        // Remove any existing listeners first
        importBtn.replaceWith(importBtn.cloneNode(true));
        const newImportBtn = document.getElementById('import-builder-btn-id');

        newImportBtn.addEventListener('click', function(e) {
            console.log('Import button clicked');
            e.preventDefault();
            e.stopPropagation();

            // Find the import file input - it's inside the button element in Gradio 5.x
            const importFileInput = document.querySelector('#import-file-input button input[type="file"]');
            console.log('Import file input found:', importFileInput);

            if (importFileInput) {
                importFileInput.click();
            } else {
                console.error('Import file input not found');
            }
        });
    }
}

// Setup drag and drop for file upload zone
function setupFileUploadDragAndDrop() {
    const fileUploadZone = document.querySelector('.file-upload-dropzone');
    if (!fileUploadZone) return;

    // Function to replace the text
    function replaceDropText() {
        const wrapDivs = document.querySelectorAll('.file-upload-dropzone .wrap');
        wrapDivs.forEach(wrapDiv => {
            if (wrapDiv.textContent.includes('Drop File Here')) {
                wrapDiv.childNodes.forEach(node => {
                    if (node.nodeType === Node.TEXT_NODE && node.textContent.includes('Drop File Here')) {
                        node.textContent = node.textContent.replace('Drop File Here', 'Drop Word or Text File Here');
                    }
                });
            }
            // Also handle the draft tab text
            if (wrapDiv.textContent.includes('Drop File Here')) {
                wrapDiv.childNodes.forEach(node => {
                    if (node.nodeType === Node.TEXT_NODE && node.textContent.includes('Drop File Here')) {
                        node.textContent = node.textContent.replace('Drop File Here', 'Drop Word or Text File Here');
                    }
                });
            }
        });
    }

    // Try to replace immediately
    replaceDropText();

    // Watch for changes in case the content is dynamically updated
    const observer = new MutationObserver((mutations) => {
        replaceDropText();
    });

    observer.observe(fileUploadZone, {
        childList: true,
        subtree: true,
        characterData: true
    });

    // Stop observing after 5 seconds to avoid performance issues
    setTimeout(() => observer.disconnect(), 5000);

    // Also setup resource upload zones
    setupResourceUploadText();
    
    // Setup draft tab file upload text monitoring
    setupDraftTabFileUpload();
    
    // Function to run text replacement after card expansion
    function runTextReplacementAfterExpansion() {
        setTimeout(() => {
            console.log('Card expanded - running replaceDraftTabText()');
            const draftFileUpload = document.querySelector('.start-file-upload-dropzone');
            if (draftFileUpload) {
                const wrapDivs = draftFileUpload.querySelectorAll('.wrap');
                wrapDivs.forEach(wrapDiv => {
                    if (wrapDiv.textContent.includes('Drop File Here')) {
                        wrapDiv.childNodes.forEach(node => {
                            if (node.nodeType === Node.TEXT_NODE && node.textContent.includes('Drop File Here')) {
                                node.textContent = node.textContent.replace('Drop File Here', 'Drop Word or Text File Here');
                            }
                        });
                    }
                });
            }
        }, 200); // Delay to let expansion animation complete
    }
    
    // Add event listeners for card expansion triggers
    document.addEventListener('click', function(e) {
        // Check if click is on input/textarea or example button that might expand the card
        if (e.target.matches('input, textarea, button') || 
            e.target.closest('.doc-title-box, .doc-description-box, .start-feature-item')) {
            runTextReplacementAfterExpansion();
        }
    });
    
    document.addEventListener('focus', function(e) {
        // Check if focus is on input that might expand the card
        if (e.target.matches('input, textarea')) {
            runTextReplacementAfterExpansion();
        }
    }, true); // Use capture phase to catch focus events early

    // Add drag-over class when dragging files over the upload zone
    let dragCounter = 0;

    function addDragListeners(element) {
        element.addEventListener('dragenter', function(e) {
            e.preventDefault();
            // Only show drag-over effect if not dragging a resource
            if (!draggedResource) {
                dragCounter++;
                fileUploadZone.classList.add('drag-over');
            }
        });

        element.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            // If dragging a resource, show "not allowed" cursor
            if (draggedResource) {
                e.dataTransfer.dropEffect = 'none';
            } else {
                fileUploadZone.classList.add('drag-over');
            }
        });

        element.addEventListener('dragleave', function(e) {
            e.preventDefault();
            dragCounter--;
            if (dragCounter === 0) {
                fileUploadZone.classList.remove('drag-over');
            }
        });

        element.addEventListener('drop', function(e) {
            dragCounter = 0;
            fileUploadZone.classList.remove('drag-over');
            // Block resource drops completely
            if (draggedResource) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
            // For file drops, let Gradio handle it - don't prevent default
        });
    }

    // Add listeners to the main zone
    addDragListeners(fileUploadZone);

    // Also add to all child elements to ensure we catch all events
    const allChildren = fileUploadZone.querySelectorAll('*');
    allChildren.forEach(child => {
        addDragListeners(child);
    });

    // Watch for new elements being added and attach listeners
    const dragObserver = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1) { // Element node
                    addDragListeners(node);
                    const newChildren = node.querySelectorAll('*');
                    newChildren.forEach(child => addDragListeners(child));
                }
            });
        });
    });

    dragObserver.observe(fileUploadZone, {
        childList: true,
        subtree: true
    });

    // Stop observing after 5 seconds
    setTimeout(() => dragObserver.disconnect(), 5000);
}

// Drag and drop functionality for resources
function setupDragAndDrop() {
    console.log('Setting up drag and drop...');

    // Setup draggable resources - now look for Gradio resource components
    const resourceItems = document.querySelectorAll('.resource-item-gradio');
    console.log('Found Gradio resource items:', resourceItems.length);

    resourceItems.forEach((item, index) => {
        // Make sure the item is draggable
        item.setAttribute('draggable', 'true');

        // Just store the path on the element for reference during drag
        const pathHidden = item.querySelector('.resource-path-hidden');
        if (pathHidden) {
            const path = pathHidden.getAttribute('data-path') || pathHidden.textContent.trim();
            item.dataset.resourcePath = path;
            console.log(`Resource ${index} path:`, path);
        }

        // Also make child elements not draggable to prevent conflicts
        const inputs = item.querySelectorAll('input, textarea, button');
        inputs.forEach(input => {
            input.setAttribute('draggable', 'false');
        });

        // Remove existing listeners to avoid duplicates
        item.removeEventListener('dragstart', handleDragStart);
        item.removeEventListener('dragend', handleDragEnd);

        // Add new listeners
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('dragend', handleDragEnd);
    });

    // Setup drop zones
    const dropZones = document.querySelectorAll('.block-resources');
    console.log('Found drop zones:', dropZones.length);

    if (dropZones.length === 0) {
        console.warn('No drop zones found! Blocks might not be rendered yet.');
        // Try again after a short delay
        setTimeout(() => {
            const retryDropZones = document.querySelectorAll('.block-resources');
            console.log('Retry - Found drop zones:', retryDropZones.length);
            setupDropZones(retryDropZones);
        }, 500);
    } else {
        setupDropZones(dropZones);
    }
}

function setupDropZones(dropZones) {
    dropZones.forEach((zone, index) => {
        // Remove existing listeners to avoid duplicates
        zone.removeEventListener('dragenter', handleDragEnter);
        zone.removeEventListener('dragover', handleDragOver);
        zone.removeEventListener('drop', handleDrop);
        zone.removeEventListener('dragleave', handleDragLeave);

        // Add new listeners
        zone.addEventListener('dragenter', handleDragEnter);
        zone.addEventListener('dragover', handleDragOver);
        zone.addEventListener('drop', handleDrop);
        zone.addEventListener('dragleave', handleDragLeave);

        // Add data attribute to help debug
        zone.setAttribute('data-drop-zone-index', index);
        console.log(`Set up drop zone ${index} on element:`, zone);
    });
}

let draggedResource = null;

function handleDragStart(e) {
    console.log('handleDragStart called on:', e.target);

    // Prevent dragging when clicking on input elements
    if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON') {
        e.preventDefault();
        return;
    }

    // For Gradio components, we need to extract data differently
    const resourceElement = e.target.closest('.resource-item-gradio');
    if (resourceElement) {
        console.log('Resource element found:', resourceElement);

        // Always extract current values dynamically to get latest updates
        console.log('Extracting current resource data...');

        // Look for elements - Gradio might have nested structures
        const titleInput = resourceElement.querySelector('.resource-title-gradio input[type="text"], .resource-title-gradio textarea');
        const descInput = resourceElement.querySelector('.resource-desc-gradio textarea');
        const pathDiv = resourceElement.querySelector('.resource-path-hidden');
        const filenameDiv = resourceElement.querySelector('.resource-filename');

        // Debug logging
        console.log('Title input found:', !!titleInput);
        if (titleInput) {
            console.log('Title input type:', titleInput.tagName);
            console.log('Title value:', titleInput.value);
        }

        console.log('Found elements:', {
            titleInput: !!titleInput,
            descInput: !!descInput,
            pathDiv: !!pathDiv,
            filenameDiv: !!filenameDiv
        });

        if (pathDiv && filenameDiv) {
            const path = pathDiv.getAttribute('data-path') || pathDiv.textContent.trim();
            const filename = filenameDiv.textContent.trim();
            // Get title from input/textarea value, fallback to filename
            const title = titleInput && titleInput.value ? titleInput.value.trim() : filename;
            const description = descInput && descInput.value ? descInput.value.trim() : '';

            draggedResource = {
                name: filename,
                title: title,
                path: path,
                type: 'text',
                description: description
            };
            console.log('Dynamically extracted resource:', draggedResource);
            console.log('Title being sent:', title);
            console.log('Filename being sent:', filename);
        }

        if (draggedResource) {
            console.log('Started dragging Gradio resource:', draggedResource);
            resourceElement.classList.add('dragging');
            document.body.classList.add('dragging-resource');
            e.dataTransfer.effectAllowed = 'copy';
            e.dataTransfer.setData('text/plain', JSON.stringify(draggedResource));

            // Set global variable to ensure it persists
            window.currentDraggedResource = draggedResource;
        } else {
            console.error('Could not extract resource data for drag');
        }
    }
}

function handleDragEnd(e) {
    // For Gradio components
    const resourceElement = e.target.closest('.resource-item-gradio');
    if (resourceElement) {
        resourceElement.classList.remove('dragging');
    } else {
        e.target.classList.remove('dragging');
    }

    // Remove dragging class from body
    document.body.classList.remove('dragging-resource');

    // Clear draggedResource after a small delay to ensure drop completes
    setTimeout(() => {
        draggedResource = null;
        window.currentDraggedResource = null;
    }, 100);
}

function handleDragEnter(e) {
    e.preventDefault();
    e.stopPropagation();
    const resource = draggedResource || window.currentDraggedResource;
    console.log('DragEnter event - draggedResource:', resource);

    if (resource) {
        e.currentTarget.classList.add('drag-over');
    }
}

function handleDragOver(e) {
    // Only prevent default for valid drop zones
    if (e.currentTarget.classList.contains('block-resources')) {
        e.preventDefault();
        e.stopPropagation();

        const resource = draggedResource || window.currentDraggedResource;

        // Debug logging - reduce verbosity
        if (!e.currentTarget.dataset.loggedOnce) {
            console.log('DragOver event - draggedResource:', resource);
            console.log('DragOver target:', e.currentTarget);
            e.currentTarget.dataset.loggedOnce = 'true';
        }

        // Only show drag-over effect if we're dragging a resource from the panel
        if (resource) {
            // Try different drop effects to get the right cursor
            e.dataTransfer.dropEffect = 'copy';
            e.currentTarget.classList.add('drag-over');

            // Force cursor style
            e.currentTarget.style.cursor = 'copy';
        }
    }
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('drag-over');
    e.currentTarget.style.cursor = '';
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('drag-over');

    const resource = draggedResource || window.currentDraggedResource;

    console.log('Drop event triggered');
    console.log('Drop target:', e.currentTarget);
    console.log('Drop zone index:', e.currentTarget.getAttribute('data-drop-zone-index'));
    console.log('Dragged resource:', resource);

    if (!resource) {
        console.error('No dragged resource found');
        return;
    }

    // Find the block ID from the parent content block
    const contentBlock = e.currentTarget.closest('.content-block');
    if (!contentBlock) {
        console.error('No parent content block found');
        console.log('Current target classes:', e.currentTarget.className);
        console.log('Parent element:', e.currentTarget.parentElement);
        return;
    }

    const blockId = contentBlock.dataset.id;
    console.log('Dropping resource on block:', blockId, resource);

    // Update the block's resources
    updateBlockResources(blockId, resource);

    // Clear both variables and remove body class
    draggedResource = null;
    window.currentDraggedResource = null;
    document.body.classList.remove('dragging-resource');
}

// Function to update block resources
function updateBlockResources(blockId, resource) {
    console.log('updateBlockResources called with blockId:', blockId);
    console.log('Resource object:', resource);

    // Set the values in hidden inputs
    const blockIdInput = document.getElementById('update-resources-block-id');
    console.log('Update resources block ID input element:', blockIdInput);

    const resourceInput = document.getElementById('update-resources-input');
    console.log('Update resources input element:', resourceInput);

    if (blockIdInput && resourceInput) {
        const blockIdTextarea = blockIdInput.querySelector('textarea') || blockIdInput.querySelector('input[type="text"]');
        console.log('Block ID textarea element:', blockIdTextarea);

        const resourceTextarea = resourceInput.querySelector('textarea') || resourceInput.querySelector('input[type="text"]');
        console.log('Resource textarea element:', resourceTextarea);

        if (blockIdTextarea && resourceTextarea) {
            // Set block ID
            blockIdTextarea.value = blockId;
            console.log('Set block ID in textarea:', blockId);

            // Set resource JSON
            const resourceJson = JSON.stringify(resource);
            resourceTextarea.value = resourceJson;
            console.log('Set resource JSON in textarea:', resourceJson);

            // Dispatch input events
            console.log('Dispatching input event for block ID textarea');
            blockIdTextarea.dispatchEvent(new Event('input', { bubbles: true }));

            console.log('Dispatching input event for resource textarea');
            resourceTextarea.dispatchEvent(new Event('input', { bubbles: true }));

            // Trigger the update button
            console.log('Setting timeout to trigger update button');
            setTimeout(() => {
                const updateBtn = document.getElementById('update-resources-trigger');
                console.log('Update resources trigger button:', updateBtn);

                if (updateBtn) {
                    updateBtn.click();
                    console.log('Clicked update resources trigger button');
                } else {
                    console.error('Update resources trigger button not found!');
                }
            }, 100);
        } else {
            console.error('One or both textareas not found!');
            console.error('Block ID textarea:', blockIdTextarea);
            console.error('Resource textarea:', resourceTextarea);
        }
    } else {
        console.error('One or both input containers not found!');
        console.error('Block ID input:', blockIdInput);
        console.error('Resource input:', resourceInput);
    }
}

// Setup example selection functionality
function setupExampleSelection() {
    const exampleItems = document.querySelectorAll('.examples-dropdown-item');

    exampleItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.stopPropagation();
            const exampleId = this.getAttribute('data-example');
            console.log('Selected example:', exampleId);

            // Set the example ID in hidden input
            const exampleIdInput = document.getElementById('example-id-input');
            if (exampleIdInput) {
                const textarea = exampleIdInput.querySelector('textarea') || exampleIdInput.querySelector('input[type="text"]');
                if (textarea) {
                    textarea.value = exampleId;
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));

                    // Trigger the load example button
                    setTimeout(() => {
                        const loadExampleBtn = document.getElementById('load-example-trigger');
                        if (loadExampleBtn) {
                            loadExampleBtn.click();

                            // Removed setupResourceDescriptions() - causes phantom Gradio events
                            // setTimeout(() => {
                            //     setupResourceDescriptions();
                            //     // Doc description will be handled by the interval watcher
                            // }, 500);
                        }
                        else {
                            console.log('loadExampleBtn not found');
                        }
                    }, 100);
                }
                else {
                    console.log('textarea not found');
                }
            }
            else {
                console.log('ExampleIdInput not found');
            }

            // Hide dropdown after selection
            const dropdown = document.getElementById('examples-dropdown-id');
            if (dropdown) {
                dropdown.style.display = 'none';
                // Re-show on next hover
                setTimeout(() => {
                    dropdown.style.removeProperty('display');
                }, 300);
            }
        });
    });
}

// Debounce timer for resource titles
let titleDebounceTimers = {};

// Update resource title function with debouncing
function updateResourceTitle(resourcePath, newTitle) {
    // Create unique key for this input
    const timerKey = resourcePath;

    // Clear existing timer for this input
    if (titleDebounceTimers[timerKey]) {
        clearTimeout(titleDebounceTimers[timerKey]);
    }

    // Update data attributes on the resource item for dragging
    const resourceItems = document.querySelectorAll('.resource-item');
    resourceItems.forEach(item => {
        if (item.getAttribute('data-resource-path') === resourcePath) {
            item.setAttribute('data-resource-title', newTitle);
        }
    });

    // Immediately update all dropped resources in AI blocks with this path
    const droppedResources = document.querySelectorAll('.dropped-resource[data-resource-path]');
    droppedResources.forEach(dropped => {
        // Check if this dropped resource matches the path
        if (dropped.getAttribute('data-resource-path') === resourcePath) {
            // Find the title span and update it
            const titleSpan = dropped.querySelector('.dropped-resource-title');
            if (titleSpan) {
                titleSpan.textContent = newTitle;
            }
        }
    });

    // Set new timer with 50ms delay (0.05 seconds after user stops typing)
    titleDebounceTimers[timerKey] = setTimeout(() => {
        // Set the values in hidden inputs
        const pathInput = document.getElementById('update-title-resource-path');
        const titleInput = document.getElementById('update-title-text');

        if (pathInput && titleInput) {
            const pathTextarea = pathInput.querySelector('textarea') || pathInput.querySelector('input[type="text"]');
            const titleTextarea = titleInput.querySelector('textarea') || titleInput.querySelector('input[type="text"]');

            if (pathTextarea && titleTextarea) {
                pathTextarea.value = resourcePath;
                titleTextarea.value = newTitle;

                // Dispatch input events
                pathTextarea.dispatchEvent(new Event('input', { bubbles: true }));
                titleTextarea.dispatchEvent(new Event('input', { bubbles: true }));

                // Trigger the update button
                setTimeout(() => {
                    const updateBtn = document.getElementById('update-title-trigger');
                    if (updateBtn) {
                        updateBtn.click();
                    }
                }, 100);
            }
        }

        // Clean up timer reference
        delete titleDebounceTimers[timerKey];
    }, 50); // Wait 50ms after user stops typing
}

// Debounce timer for resource panel descriptions
let panelDescriptionDebounceTimers = {};

// Update resource description from panel with debouncing
function updateResourcePanelDescription(resourcePath, newDescription) {
    // Create unique key for this input
    const timerKey = `panel-${resourcePath}`;

    // Clear existing timer for this input
    if (panelDescriptionDebounceTimers[timerKey]) {
        clearTimeout(panelDescriptionDebounceTimers[timerKey]);
    }

    // Set new timer with 50ms delay
    panelDescriptionDebounceTimers[timerKey] = setTimeout(() => {
        // Set the values in hidden inputs - reusing the title inputs as per Python code
        const pathInput = document.getElementById('update-title-resource-path');
        const descInput = document.getElementById('update-title-text');

        if (pathInput && descInput) {
            const pathTextarea = pathInput.querySelector('textarea') || pathInput.querySelector('input[type="text"]');
            const descTextarea = descInput.querySelector('textarea') || descInput.querySelector('input[type="text"]');

            if (pathTextarea && descTextarea) {
                pathTextarea.value = resourcePath;
                descTextarea.value = newDescription;

                // Dispatch input events
                pathTextarea.dispatchEvent(new Event('input', { bubbles: true }));
                descTextarea.dispatchEvent(new Event('input', { bubbles: true }));

                // Trigger the update button for description
                setTimeout(() => {
                    const updateBtn = document.getElementById('update-panel-desc-trigger');
                    if (updateBtn) {
                        updateBtn.click();
                    }
                }, 100);
            }
        }

        // Clean up timer reference
        delete panelDescriptionDebounceTimers[timerKey];
    }, 50);
}

// Toggle resource description collapse/expand
function toggleResourceDescription(resourceId) {
    const resourceItem = document.getElementById(resourceId);
    if (resourceItem) {
        const container = resourceItem.querySelector('.resource-description-container');
        const textarea = container.querySelector('.resource-panel-description');
        const button = container.querySelector('.desc-expand-btn');

        const lineHeight = 11 * 1.4; // 11px font * 1.4 line-height
        const padding = 8; // 4px top + 4px bottom
        const twoLinesHeight = (lineHeight * 2) + padding;

        // Function to get first two lines with ellipsis
        function getFirstTwoLinesWithEllipsis(text) {
            if (!text) return '';
            const lines = text.split('\n');
            let firstTwo = lines.slice(0, 2).join('\n');

            // Add ellipsis if there's more content
            if (lines.length > 2 || (lines.length === 2 && lines[1].length > 20)) {
                firstTwo += '...';
            }
            return firstTwo;
        }

        if (container.classList.contains('collapsed')) {
            // Expand - restore original text
            container.classList.remove('collapsed');
            button.innerHTML = '⌵';
            button.title = 'Collapse';
            textarea.value = textarea.dataset.originalValue || textarea.value.replace(/\.\.\.$/,'');
            textarea.style.height = 'auto';
            textarea.style.maxHeight = '180px';
            textarea.style.overflow = ''; // Reset to CSS default
            textarea.classList.remove('scrollable');
            container.classList.remove('has-scrollbar');

            // Recalculate height and scrollability
            const scrollHeight = textarea.scrollHeight;
            textarea.style.height = Math.min(scrollHeight, 180) + 'px';
            if (scrollHeight > 180) {
                textarea.classList.add('scrollable');
                container.classList.add('has-scrollbar');
            }

            // Restore cursor position if available
            if (textarea.dataset.cursorPos) {
                const cursorPos = parseInt(textarea.dataset.cursorPos);
                textarea.focus();
                textarea.setSelectionRange(cursorPos, cursorPos);
                delete textarea.dataset.cursorPos;
            } else {
                textarea.focus();
            }
        } else {
            // Collapse - save original and show first 2 lines with ellipsis
            textarea.dataset.originalValue = textarea.value;
            container.classList.add('collapsed');
            button.innerHTML = '⌵';
            button.title = 'Expand';
            textarea.value = getFirstTwoLinesWithEllipsis(textarea.dataset.originalValue);
            textarea.style.height = twoLinesHeight + 'px';
            textarea.style.maxHeight = twoLinesHeight + 'px';
            textarea.style.overflow = 'hidden';
            textarea.classList.remove('scrollable');
            container.classList.remove('has-scrollbar');
            textarea.blur();
        }
    }
}

// Setup auto-expand for resource descriptions
function setupResourceDescriptions() {
    // Handle Gradio resource descriptions
    const gradioDescTextareas = document.querySelectorAll('.resource-desc-gradio textarea');

    gradioDescTextareas.forEach(textarea => {
        const container = textarea.closest('.resource-desc-gradio');
        if (!container || container.dataset.toggleSetup) {
            return;
        }

        // Mark as setup
        container.dataset.toggleSetup = 'true';

        // Create expand/collapse button
        const button = document.createElement('button');
        button.className = 'desc-expand-btn';
        button.innerHTML = '⌵'; // Down chevron
        button.title = 'Collapse';
        button.style.display = 'none'; // Hidden by default

        // Add button to container
        container.appendChild(button);

        // Track collapsed state and full text
        let isCollapsed = false;
        let fullText = '';

        // Function to get first two lines of text
        function getFirstTwoLines(text) {
            const lines = text.split('\n');

            // Always show exactly 2 lines
            if (lines.length === 1) {
                // If only one line, just return it with ellipsis if it's long
                return lines[0].length > 50 ? lines[0].substring(0, 47) + '...' : lines[0];
            } else if (lines.length >= 2) {
                // Get exactly first two lines
                const firstLine = lines[0];
                const secondLine = lines[1];

                // If there are more than 2 lines or the second line is long, add ellipsis
                if (lines.length > 2 || secondLine.length > 50) {
                    // Truncate second line if needed to make room for ellipsis
                    const truncatedSecond = secondLine.length > 47 ? secondLine.substring(0, 47) : secondLine;
                    return firstLine + '\n' + truncatedSecond + '...';
                } else {
                    return firstLine + '\n' + secondLine;
                }
            }

            return text;
        }

        // Function to check if button should be visible
        function checkButtonVisibility() {
            if (isCollapsed) return;

            // Count actual lines in the textarea
            const lines = textarea.value.split('\n');
            let totalLines = lines.length; // Start with actual line breaks

            // Add wrapped lines - more accurate estimation
            // Resource panel is narrower, estimate ~35 chars per line at 11px font
            lines.forEach((line, index) => {
                if (line.length > 35) {
                    // Add extra lines for wrapping
                    totalLines += Math.floor(line.length / 35);
                }
            });

            // Show button if content exceeds 2 lines
            if (totalLines > 2) {
                button.style.display = 'block';
            } else {
                button.style.display = 'none';
            }

            // Set rows attribute based on content, no max
            let rowsToShow = Math.max(2, totalLines);

            // Add 1 extra row if we have 3 or more rows for breathing room
            if (rowsToShow >= 3) {
                rowsToShow += 1;
            }

            textarea.rows = rowsToShow;
            textarea.style.height = ''; // Let rows attribute control height
            textarea.style.minHeight = ''; // Clear any min-height
            textarea.style.maxHeight = ''; // Clear any max-height
            textarea.style.overflow = 'hidden'; // No scrollbars

            // Never add scrollable class
            textarea.classList.remove('scrollable');
        }

        // Toggle collapse/expand
        function toggleCollapse() {
            if (isCollapsed) {
                // Expand
                textarea.value = fullText;
                textarea.style.height = ''; // Clear height to let rows control it
                container.classList.remove('collapsed');
                button.innerHTML = '⌵';
                button.title = 'Collapse';
                isCollapsed = false;
                // Don't set rows to null - let checkButtonVisibility set it
                checkButtonVisibility();
                textarea.focus();

                // Trigger input event to update Gradio's state
                textarea.dispatchEvent(new Event('input', { bubbles: true }));
            } else {
                // Collapse
                fullText = textarea.value;
                textarea.value = getFirstTwoLines(fullText);
                textarea.rows = 2; // Force exactly 2 rows
                textarea.style.height = ''; // Let rows attribute control height
                container.classList.add('collapsed');
                button.innerHTML = '⌵';
                button.title = 'Expand';
                isCollapsed = true;
                textarea.classList.remove('scrollable');
                textarea.blur();
            }
        }

        // Button click handler
        button.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            toggleCollapse();
        });

        // Click on collapsed textarea to expand
        textarea.addEventListener('click', (e) => {
            if (isCollapsed) {
                const cursorPos = textarea.selectionStart;
                toggleCollapse();
                setTimeout(() => {
                    textarea.setSelectionRange(cursorPos, cursorPos);
                }, 0);
            }
        });

        // Check on input
        textarea.addEventListener('input', () => {
            checkButtonVisibility();
            if (isCollapsed) {
                toggleCollapse();
            }
        });

        // Initial check
        checkButtonVisibility();

        // If textarea has initial content, ensure proper display
        if (textarea.value && textarea.value.split('\n').length > 2) {
            checkButtonVisibility();
        }

        // Watch for value changes (e.g., from imports)
        const observer = new MutationObserver(() => {
            if (!isCollapsed && textarea.value !== fullText) {
                checkButtonVisibility();
            }
        });

        observer.observe(textarea, {
            attributes: true,
            attributeFilter: ['value']
        });

        // Also listen for programmatic value changes
        let lastValue = textarea.value;
        setInterval(() => {
            if (textarea.value !== lastValue && !isCollapsed) {
                lastValue = textarea.value;
                checkButtonVisibility();
            }
        }, 500);
    });

    // Also handle the old panel descriptions if they exist
    const descTextareas = document.querySelectorAll('.resource-panel-description');

    descTextareas.forEach(textarea => {
        // Store original value without ellipsis
        if (!textarea.dataset.originalValue) {
            textarea.dataset.originalValue = textarea.value;
        }

        // Set minimum height for 2 lines
        const lineHeight = 11 * 1.4; // 11px font * 1.4 line-height
        const padding = 8; // 4px top + 4px bottom
        const minHeight = (lineHeight * 2) + padding;
        textarea.style.minHeight = minHeight + 'px';

        // Function to get first two lines with ellipsis
        function getFirstTwoLinesWithEllipsis(text) {
            if (!text) return '';
            const lines = text.split('\n');
            let firstTwo = lines.slice(0, 2).join('\n');

            // Add ellipsis if there's more content
            if (lines.length > 2 || (lines.length === 2 && lines[1].length > 20)) {
                firstTwo += '...';
            }
            return firstTwo;
        }

        // Auto-expand handler
        const autoExpand = function() {
            const container = this.closest('.resource-description-container');
            const button = container.querySelector('.desc-expand-btn');
            const isCollapsed = container.classList.contains('collapsed');

            // Store original value if typing
            if (!isCollapsed && this === document.activeElement) {
                this.dataset.originalValue = this.value;
            }

            if (!isCollapsed) {
                // Reset height to auto to get correct scrollHeight
                this.style.height = 'auto';
                const scrollHeight = this.scrollHeight;

                // Set height to scrollHeight, capped at max-height (180px)
                const newHeight = Math.min(scrollHeight, 180);
                this.style.height = newHeight + 'px';

                // Add scrollable class only if content exceeds 10 lines
                // Check against newHeight (before capping) to show scrollbar when starting 11th line
                const lineHeight = 11 * 1.4; // 11px font * 1.4 line-height
                const padding = 8; // 4px top + 4px bottom
                const tenLinesHeight = (lineHeight * 10) + padding;

                if (this.style.height === 'auto' && this.scrollHeight > tenLinesHeight) {
                    this.classList.add('scrollable');
                    container.classList.add('has-scrollbar');
                } else if (parseFloat(this.style.height) >= 180) {
                    // Also check if we're at max height
                    this.classList.add('scrollable');
                    container.classList.add('has-scrollbar');
                } else {
                    this.classList.remove('scrollable');
                    container.classList.remove('has-scrollbar');
                }

                // Check button visibility - moved inside the !isCollapsed block
                // Get actual computed line height and padding
                const computedLineHeight = parseFloat(window.getComputedStyle(this).lineHeight);
                const computedPadding = parseInt(window.getComputedStyle(this).paddingTop) +
                                       parseInt(window.getComputedStyle(this).paddingBottom);
                const computedTwoLinesHeight = (computedLineHeight * 2) + computedPadding;

                // Reset height temporarily to get accurate scrollHeight
                const currentHeight = this.style.height;
                this.style.height = 'auto';
                const actualScrollHeight = this.scrollHeight;
                this.style.height = currentHeight;

                // Count actual lines of text
                const lines = this.value.split('\n');
                let actualLineCount = 0;
                for (let line of lines) {
                    // Count wrapped lines too - approximate based on line length
                    // Resource panel is about 170px wide, ~15-20 chars per line at 11px font
                    actualLineCount += 1 + Math.floor(line.length / 20);
                }

                // Show button only when starting the 3rd line (similar to doc description)
                // Don't use trim() - count empty lines too
                if (actualLineCount > 2) {
                    button.style.display = 'block';
                } else {
                    button.style.display = 'none';
                    container.classList.remove('collapsed');
                }
            }
        };

        // Add event listeners
        textarea.addEventListener('input', autoExpand);
        textarea.addEventListener('paste', function() {
            setTimeout(() => autoExpand.call(this), 10);
        });

        // Click to expand when collapsed
        textarea.addEventListener('click', function(e) {
            const container = this.closest('.resource-description-container');
            if (container.classList.contains('collapsed')) {
                // Get cursor position before expanding
                const cursorPos = this.selectionStart;
                const resourceId = container.closest('.resource-item').id;

                // Store cursor position in dataset to use after expansion
                this.dataset.cursorPos = cursorPos;

                toggleResourceDescription(resourceId);
            }
        });

        // Initial sizing
        autoExpand.call(textarea);
    });
}

// Handle resource file upload
function handleResourceFileUpload(resourcePath, fileInput) {
    const file = fileInput.files[0];
    if (!file) return;

    console.log('Uploading file to replace resource:', resourcePath, file.name);

    // Set the resource path
    const pathInput = document.getElementById('replace-resource-path');
    if (pathInput) {
        const pathTextarea = pathInput.querySelector('textarea') || pathInput.querySelector('input[type="text"]');
        if (pathTextarea) {
            pathTextarea.value = resourcePath;
            pathTextarea.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    // Find the hidden file input component and set the file
    const hiddenFileInput = document.querySelector('#replace-resource-file input[type="file"]');
    if (hiddenFileInput) {
        // Create a new DataTransfer to set files on the hidden input
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        hiddenFileInput.files = dataTransfer.files;

        // Trigger change event on the hidden file input
        hiddenFileInput.dispatchEvent(new Event('change', { bubbles: true }));

        // Trigger the replace button after a delay
        setTimeout(() => {
            const replaceBtn = document.getElementById('replace-resource-trigger');
            if (replaceBtn) {
                replaceBtn.click();

                // Add visual feedback to the upload zone
                const uploadZone = fileInput.closest('.resource-upload-zone');
                if (uploadZone) {
                    uploadZone.classList.add('upload-success');
                    const uploadText = uploadZone.querySelector('.upload-text');
                    if (uploadText) {
                        uploadText.textContent = '✓ File replaced';
                    }

                    // Reset after 2 seconds
                    setTimeout(() => {
                        uploadZone.classList.remove('upload-success');
                        uploadText.textContent = 'Drop file here to replace';
                    }, 2000);
                }
            }
        }, 100);
    }

    // Clear the file input
    fileInput.value = '';
}

// Prevent drops on resource textareas and inputs
function preventResourceDrops() {
    // Prevent drops on all textareas and inputs within resource items
    const resourceInputs = document.querySelectorAll('.resource-item input, .resource-item textarea');

    resourceInputs.forEach(element => {
        element.addEventListener('dragover', function(e) {
            e.preventDefault();
            if (draggedResource) {
                e.dataTransfer.dropEffect = 'none';
            }
        });

        element.addEventListener('drop', function(e) {
            e.preventDefault();
            if (draggedResource) {
                e.stopPropagation();
                return false;
            }
        });
    });
}

// Function to setup resource upload text
function setupResourceUploadText() {
    // Function to replace the text in resource upload zones
    function replaceResourceUploadText() {
        const resourceUploadZones = document.querySelectorAll('.resource-upload-gradio');

        resourceUploadZones.forEach(zone => {
            // Find all text nodes and remove default Gradio text
            const wrapDivs = zone.querySelectorAll('.wrap');
            wrapDivs.forEach(wrapDiv => {
                // Hide the icon
                const icon = wrapDiv.querySelector('.icon-wrap');
                if (icon) {
                    icon.style.display = 'none';
                }

                // Replace the text content and remove spans with "- or -"
                wrapDiv.childNodes.forEach(node => {
                    if (node.nodeType === Node.TEXT_NODE) {
                        const text = node.textContent;
                        if (text.includes('Drop File Here') || text.includes('Click to Upload') || text.includes('- or -')) {
                            node.textContent = '';
                        }
                    } else if (node.nodeType === Node.ELEMENT_NODE && node.tagName === 'SPAN') {
                        // Check if span contains "- or -" or other unwanted text
                        if (node.textContent.includes('- or -') ||
                            node.textContent.includes('Drop File Here') ||
                            node.textContent.includes('Click to Upload')) {
                            node.style.display = 'none';
                        }
                    }
                });

                // Also hide any .or class spans
                const orSpans = wrapDiv.querySelectorAll('.or, span.or');
                orSpans.forEach(span => {
                    span.style.display = 'none';
                });

                // Add our custom text if not already present
                if (!wrapDiv.querySelector('.custom-upload-text')) {
                    const customText = document.createElement('span');
                    customText.className = 'custom-upload-text';
                    customText.textContent = 'Drop file here to replace';
                    customText.style.fontSize = '11px';
                    customText.style.color = '#666';
                    wrapDiv.appendChild(customText);
                }
            });
        });
    }

    // Try to replace immediately
    replaceResourceUploadText();

    // Watch for changes in resource areas
    const resourcesArea = document.querySelector('.resources-display-area');
    if (resourcesArea) {
        const observer = new MutationObserver((mutations) => {
            replaceResourceUploadText();
        });

        observer.observe(resourcesArea, {
            childList: true,
            subtree: true
        });

        // Stop observing after 10 seconds
        setTimeout(() => observer.disconnect(), 10000);
    }
}

// Setup drag and drop for resource upload zones
function setupResourceUploadZones() {
    const uploadZones = document.querySelectorAll('.resource-upload-zone');

    uploadZones.forEach(zone => {
        let dragCounter = 0;

        zone.addEventListener('dragenter', function(e) {
            e.preventDefault();
            // Only show drag-over effect if NOT dragging a resource
            if (!draggedResource) {
                dragCounter++;
                this.classList.add('drag-over');
            }
        });

        zone.addEventListener('dragover', function(e) {
            e.preventDefault();
            // If dragging a resource, show "not allowed" cursor
            if (draggedResource) {
                e.dataTransfer.dropEffect = 'none';
            } else {
                // For external files, show "copy" cursor
                e.dataTransfer.dropEffect = 'copy';
            }
        });

        zone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            dragCounter--;
            if (dragCounter === 0) {
                this.classList.remove('drag-over');
            }
        });

        zone.addEventListener('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dragCounter = 0;
            this.classList.remove('drag-over');

            // Block resource drops completely
            if (draggedResource) {
                return false;
            }

            // Handle external file drops
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                const fileInput = this.querySelector('.resource-file-input');
                const resourcePath = this.getAttribute('data-resource-path');

                if (fileInput && resourcePath) {
                    // Create a new DataTransfer to set files on input
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(e.dataTransfer.files[0]);
                    fileInput.files = dataTransfer.files;

                    // Trigger the change event
                    handleResourceFileUpload(resourcePath, fileInput);
                }
            }
        });
    });
}

// Setup draft tab file upload text monitoring
function setupDraftTabFileUpload() {
    console.log('🔧 setupDraftTabFileUpload() called');
    
    // Function to replace the draft tab text
    function replaceDraftTabText() {
        console.log('🔍 replaceDraftTabText() called');
        const draftFileUpload = document.querySelector('.start-file-upload-dropzone');
        console.log('📁 Found start-file-upload-dropzone:', !!draftFileUpload);

        if (draftFileUpload) {
            const wrapDivs = draftFileUpload.querySelectorAll('.wrap');
            console.log('📦 Found wrap divs:', wrapDivs.length);
            
            wrapDivs.forEach((wrapDiv, index) => {
                console.log(`📝 Wrap div ${index} text:`, wrapDiv.textContent);
                
                if (wrapDiv.textContent.includes('Drop File Here')) {
                    console.log('✅ Found "Drop File Here" in wrap div', index);
                    wrapDiv.childNodes.forEach((node, nodeIndex) => {
                        if (node.nodeType === Node.TEXT_NODE && node.textContent.includes('Drop File Here')) {
                            console.log(`🔄 Replacing text in node ${nodeIndex}:`, node.textContent);
                            node.textContent = node.textContent.replace('Drop File Here', 'Drop Word or Text File Here');
                            console.log(`✨ New text:`, node.textContent);
                        }
                    });
                } else {
                    console.log('❌ No "Drop File Here" found in wrap div', index);
                }
            });
        } else {
            console.log('❌ No start-file-upload-dropzone found');
        }
    }

    // Try to replace immediately in case it's already visible
    console.log('🚀 Running initial replaceDraftTabText()');
    replaceDraftTabText();

    // Watch for the entire document body for changes since the draft tab components appear dynamically
    const observer = new MutationObserver((mutations) => {
        console.log('👀 MutationObserver triggered, mutations:', mutations.length);
        
        mutations.forEach((mutation, mutIndex) => {
            console.log(`🔄 Mutation ${mutIndex} type: ${mutation.type}`);
            
            if (mutation.type === 'childList') {
                console.log(`📝 childList - added: ${mutation.addedNodes.length}, removed: ${mutation.removedNodes.length}`);
                
                // Check if any added nodes contain file upload components
                mutation.addedNodes.forEach((node, nodeIndex) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        console.log(`🧩 Added Node ${nodeIndex}:`, node.tagName, node.className);
                        
                        // Check if this node or its children contain the file upload dropzone
                        if (node.classList && node.classList.contains('file-upload-dropzone')) {
                            console.log('🎯 Found file-upload-dropzone as added node!');
                            setTimeout(replaceDraftTabText, 100);
                        } else if (node.querySelector && node.querySelector('.file-upload-dropzone')) {
                            console.log('🎯 Found file-upload-dropzone inside added node!');
                            setTimeout(replaceDraftTabText, 100);
                        }
                    } else {
                        console.log(`📄 Added text node ${nodeIndex}:`, node.textContent?.substring(0, 50));
                    }
                });
            } else if (mutation.type === 'attributes') {
                console.log(`🏷️ Attribute change on:`, mutation.target.tagName, mutation.target.className, 'attr:', mutation.attributeName);
                
                // Check if visibility/style attributes changed on file upload elements
                if (mutation.target.classList && mutation.target.classList.contains('file-upload-dropzone')) {
                    console.log('🎯 File upload dropzone attribute changed!');
                    setTimeout(replaceDraftTabText, 100);
                } else if (mutation.target.querySelector && mutation.target.querySelector('.file-upload-dropzone')) {
                    console.log('🎯 Element with file upload dropzone had attribute change!');
                    setTimeout(replaceDraftTabText, 100);
                }
            }
        });
        
        // Also try replacing text after any mutation
        setTimeout(replaceDraftTabText, 200);
    });

    // Observe the entire document body for changes
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class', 'style', 'hidden']
    });
    console.log('👁️ MutationObserver started on document.body');

    // Cleanup observer after a reasonable time to avoid memory leaks
    setTimeout(() => {
        observer.disconnect();
        console.log('🛑 MutationObserver disconnected after 30 seconds');
    }, 30000); // 30 seconds
}

// Function to remove a resource from the Start tab
function removeStartResourceByIndex(index, resourceName) {
    console.log('removeStartResourceByIndex called with index:', index, 'resourceName:', resourceName);
    
    // Prevent the card from collapsing
    const expandableSection = document.getElementById('start-expandable-section');
    const wasExpanded = expandableSection && expandableSection.classList.contains('expanded');
    console.log('DEBUG: expandableSection found:', !!expandableSection, 'wasExpanded:', wasExpanded);

    // Find the hidden inputs for start tab resource removal
    const indexInput = document.getElementById('start-remove-resource-index');
    const nameInput = document.getElementById('start-remove-resource-name');
    console.log('DEBUG: indexInput found:', !!indexInput, 'nameInput found:', !!nameInput);

    if (indexInput && nameInput) {
        // Find the actual input elements (Gradio wraps them)
        const indexTextarea = indexInput.querySelector('textarea') || indexInput.querySelector('input[type="text"]');
        const nameTextarea = nameInput.querySelector('textarea') || nameInput.querySelector('input[type="text"]');
        console.log('DEBUG: indexTextarea found:', !!indexTextarea, 'nameTextarea found:', !!nameTextarea);

        if (indexTextarea && nameTextarea) {
            // Set the values
            indexTextarea.value = index.toString();
            nameTextarea.value = resourceName;
            console.log('DEBUG: Set index value:', indexTextarea.value, 'name value:', nameTextarea.value);

            // Dispatch input events to trigger Gradio update
            indexTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            nameTextarea.dispatchEvent(new Event('input', { bubbles: true }));
            console.log('DEBUG: Dispatched input events');

            // Find and click the remove button
            const removeBtn = document.getElementById('start-remove-resource-btn');
            console.log('DEBUG: removeBtn found:', !!removeBtn);
            console.log('DEBUG: removeBtn element:', removeBtn);
            
            if (removeBtn) {
                console.log('DEBUG: About to click remove button');
                removeBtn.click();
                console.log('Clicked remove button');
                
                // Ensure the card stays expanded if it was expanded
                if (wasExpanded) {
                    setTimeout(() => {
                        if (expandableSection && !expandableSection.classList.contains('expanded')) {
                            expandableSection.classList.add('expanded');
                            expandableSection.style.removeProperty('display');
                            expandableSection.style.removeProperty('opacity');
                            const card = document.querySelector('.start-input-card');
                            if (card) card.classList.add('has-expanded');
                        }
                    }, 100);
                }
            } else {
                console.error('DEBUG: Remove button not found! Looking for alternatives...');
                
                // Try to find button by other methods
                const allButtons = document.querySelectorAll('button');
                console.log('DEBUG: Total buttons in DOM:', allButtons.length);
                
                let foundButton = null;
                allButtons.forEach((btn, idx) => {
                    if (btn.id === 'start-remove-resource-btn') {
                        console.log('DEBUG: Found button by ID at index:', idx);
                        foundButton = btn;
                    }
                });
                
                if (foundButton) {
                    console.log('DEBUG: Clicking found button');
                    foundButton.click();
                    console.log('Clicked remove button (fallback method)');
                } else {
                    console.error('DEBUG: Could not find remove button by any method');
                    
                    // List all elements with IDs containing 'start-remove'
                    const startRemoveElements = document.querySelectorAll('[id*="start-remove"]');
                    console.log('DEBUG: Elements with start-remove in ID:', startRemoveElements.length);
                    startRemoveElements.forEach((el, idx) => {
                        console.log(`DEBUG: start-remove element ${idx}: ID=${el.id}, tag=${el.tagName}`);
                    });
                }
            }
        } else {
            console.error('DEBUG: Could not find input textareas');
            console.error('DEBUG: indexInput content:', indexInput ? indexInput.innerHTML : 'null');
            console.error('DEBUG: nameInput content:', nameInput ? nameInput.innerHTML : 'null');
        }
    } else {
        console.error('DEBUG: Could not find input containers');
        
        // List all elements with IDs containing 'start-remove'
        const startRemoveElements = document.querySelectorAll('[id*="start-remove"]');
        console.log('DEBUG: All start-remove elements:', startRemoveElements.length);
        startRemoveElements.forEach((el, idx) => {
            console.log(`DEBUG: Element ${idx}: ID=${el.id}, tag=${el.tagName}`);
        });
    }
}


// Call setup on initial load
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOMContentLoaded - Starting initialization');

    refresh();
    console.log('Called refresh()');

    setupImportButton();
    console.log('Called setupImportButton()');

    // Upload resource setup no longer needed - using Gradio's native component
    setupExampleSelection();
    console.log('Called setupExampleSelection()');

    // Delay initial drag and drop setup
    setTimeout(() => {
        console.log('Starting delayed setup functions');

        setupDragAndDrop();
        console.log('Called setupDragAndDrop()');

        // Removed setupResourceDescriptions() - causes phantom Gradio events
        // console.log('Called setupResourceDescriptions()');

        setupResourceTitleObservers();
        console.log('Called setupResourceTitleObservers()');

        setupResourceUploadZones();
        console.log('Called setupResourceUploadZones()');

        setupResourceUploadText();
        console.log('Called setupResourceUploadText()');

        preventResourceDrops();
        console.log('Called preventResourceDrops()');

        setupHowItWorksHover();
        console.log('Called setupHowItWorksHover()');

        console.log('All initialization complete');
    }, 100);
});

// Handle How It Works section hover effects
function setupHowItWorksHover() {
    const steps = document.querySelectorAll('.start-process-step-vertical');
    
    if (steps.length === 3) {
        console.log('Setting up How It Works hover effects');
        
        // Set step 1 as active by default
        steps[0].classList.add('active');
        
        steps.forEach((step, index) => {
            step.addEventListener('mouseenter', () => {
                // Remove active from all steps
                steps.forEach(s => s.classList.remove('active'));
                // Add active to hovered step
                step.classList.add('active');
            });
        });
        
        // When not hovering any step, default to step 1
        const container = document.querySelector('.start-process-steps-vertical');
        if (container) {
            container.addEventListener('mouseleave', () => {
                steps.forEach(s => s.classList.remove('active'));
                steps[0].classList.add('active');
            });
        }
    } else {
        console.log('How It Works steps not found or incorrect count:', steps.length);
    }
}

