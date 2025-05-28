"""
Just 5 main callbacks instead of 15+.
"""
from document_generator_app.models.outline import Outline, Resource, Section
from document_generator_app.ui.utils import (
    get_section_at_path, 
    add_section_at_path, 
    remove_section_at_path
)


def create_initial_state():
    """Create initial app state."""
    return {
        "outline": Outline(title="", general_instruction=""),
        "selected_type": None,     # "resource" or "section"
        "selected_id": None,        # e.g., "resource_0" or "section_1_2"
    }


def select_item(item_id: str, item_type: str, state: dict) -> dict:
    """Handle clicking on a list item."""
    state["selected_id"] = item_id
    state["selected_type"] = item_type
    return state


def add_resource(state: dict) -> dict:
    """Add new resource and select it."""
    state["outline"].resources.append(
        Resource(key="", path="", description="", merge_mode="concat")
    )
    state["selected_id"] = f"resource_{len(state['outline'].resources) - 1}"
    state["selected_type"] = "resource"
    return state


def add_section(state: dict, as_subsection: bool = False) -> dict:
    """Add new section (top-level or as subsection of selected)."""
    new_section = Section(title="New Section")
    
    if as_subsection and state["selected_type"] == "section":
        # Add as subsection of selected section
        path_str = state["selected_id"].split("_")[1:]
        path = [int(p) for p in path_str]
        
        # Check if we're within depth limit (max 4 levels)
        if len(path) < 4:
            add_section_at_path(state["outline"].sections, path, new_section)
            # Update selection to the new subsection
            parent = get_section_at_path(state["outline"].sections, path)
            if parent and hasattr(parent, 'sections') and parent.sections:
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
                if parent and hasattr(parent, 'sections'):
                    insert_idx = path[-1] + 1
                    parent.sections.insert(insert_idx, new_section)
                    state["selected_id"] = f"section_{'_'.join([str(p) for p in parent_path] + [str(insert_idx)])}"
        else:
            # No section selected - add to end of top-level
            state["outline"].sections.append(new_section)
            state["selected_id"] = f"section_{len(state['outline'].sections) - 1}"
    
    state["selected_type"] = "section"
    return state


def save_item(form_data: dict, state: dict) -> dict:
    """Save changes to selected item."""
    if not state["selected_id"]:
        return state
    
    if state["selected_type"] == "resource":
        idx = int(state["selected_id"].split("_")[1])
        if idx < len(state["outline"].resources):
            res = state["outline"].resources[idx]
            res.key = form_data.get("key", "")
            res.description = form_data.get("description", "")
            
            # Handle file upload vs path
            if form_data.get("file"):
                # Gradio returns file path as string
                res.path = form_data["file"]
            else:
                res.path = form_data.get("path", "")
            
            res.merge_mode = form_data.get("merge_mode", "concat")
            
    elif state["selected_type"] == "section":
        path_str = state["selected_id"].split("_")[1:]
        path = [int(p) for p in path_str]
        sec = get_section_at_path(state["outline"].sections, path)
        
        if sec:
            sec.title = form_data.get("title", "")
            
            if form_data.get("mode") == "Prompt":
                sec.prompt = form_data.get("prompt", "")
                sec.refs = form_data.get("refs", [])
                # Clear static mode fields
                sec.resource_key = None
            else:  # Static mode
                sec.resource_key = form_data.get("resource_key", "")
                # Clear prompt mode fields
                sec.prompt = None
                sec.refs = []
    
    return state


def remove_selected(state: dict) -> dict:
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