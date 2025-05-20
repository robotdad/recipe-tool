"""
UI package for Document Generator.
"""

__all__ = ["build_editor", "resource_entry", "section_entry"]
from .layout import build_editor
from .components import resource_entry, section_entry
