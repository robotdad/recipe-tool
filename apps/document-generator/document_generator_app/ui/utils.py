"""
Simple utility functions for the Document Generator UI.
"""

from document_generator_app.models.outline import Outline
from document_generator_app.schema.validator import validate_outline


def validate_outline_data(outline: Outline) -> tuple[bool, str]:
    """
    Validate an outline and return (is_valid, message).
    """
    try:
        validate_outline(outline.dict())
        return True, "Outline is valid"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def get_section_at_path(sections: list, path: list[int]):
    """
    Navigate to a section using a path of indices.
    Example: path=[1, 2] returns sections[1].sections[2]
    Returns a Section object or None.
    """
    current = sections
    for i, idx in enumerate(path):
        if idx >= len(current):
            return None
        if i == len(path) - 1:
            return current[idx]
        current = current[idx].sections
    return None


def set_section_at_path(sections: list, path: list[int], new_section) -> None:
    """
    Update a section at the given path.
    """
    if not path:
        return
    
    current = sections
    for i, idx in enumerate(path[:-1]):
        if idx >= len(current):
            return
        current = current[idx].sections
    
    if path[-1] < len(current):
        current[path[-1]] = new_section


def add_section_at_path(sections: list, path: list[int], new_section) -> None:
    """
    Add a section as a subsection at the given path.
    """
    if not path:
        sections.append(new_section)
        return
    
    parent = get_section_at_path(sections, path)
    if parent:
        if not hasattr(parent, 'sections') or parent.sections is None:
            parent.sections = []
        parent.sections.append(new_section)


def remove_section_at_path(sections: list, path: list[int]) -> None:
    """
    Remove a section at the given path.
    """
    if not path:
        return
    
    if len(path) == 1:
        if path[0] < len(sections):
            sections.pop(path[0])
    else:
        parent_path = path[:-1]
        parent = get_section_at_path(sections, parent_path)
        if parent and hasattr(parent, 'sections') and parent.sections:
            if path[-1] < len(parent.sections):
                parent.sections.pop(path[-1])


def clean_refs(refs: list[str], valid_keys: list[str]) -> list[str]:
    """
    Remove any refs that don't exist in valid_keys.
    """
    if not refs:
        return []
    return [ref for ref in refs if ref in valid_keys]