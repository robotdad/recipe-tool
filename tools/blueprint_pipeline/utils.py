#!/usr/bin/env python3
"""
Utilities module for the blueprint pipeline.

This module contains utility functions for the blueprint pipeline,
such as logging, file operations, and miscellaneous helpers.
"""
import glob
import os
import threading
from typing import Optional


# Global print lock to prevent output interleaving
print_lock = threading.Lock()


def safe_print(*args, **kwargs):
    """
    Thread-safe print function to prevent output interleaving in parallel processing.

    Args:
        *args: Arguments to pass to the print function.
        **kwargs: Keyword arguments to pass to the print function.
    """
    with print_lock:
        print(*args, **kwargs)


def find_latest_spec(component_id: str, output_dir: str) -> Optional[str]:
    """
    Find the latest specification file for a component.

    Looks first in the clarification directory for revised specs,
    then in the components directory for original specs.

    Args:
        component_id: ID of the component.
        output_dir: Root output directory.

    Returns:
        Optional[str]: Path to the latest specification file, or None if not found.
    """
    # Check for revised specs first
    revised_specs = glob.glob(f"{output_dir}/clarification/{component_id}_candidate_spec_revised.md")
    if revised_specs:
        # Sort by modification time to get the latest one
        return sorted(revised_specs, key=os.path.getmtime)[-1]

    # Then check original specs
    original_specs = glob.glob(f"{output_dir}/components/{component_id}_candidate_spec.md")
    if original_specs:
        return original_specs[0]

    return None


def needs_human_review(eval_file_path: str) -> bool:
    """
    Check if an evaluation file indicates the specification needs human review.

    Args:
        eval_file_path: Path to the evaluation file.

    Returns:
        bool: True if the specification needs human review, False otherwise.
    """
    return "_needs_clarification" in eval_file_path


def copy_files_to_human_review(files: list, source_dir: str, dest_dir: str) -> None:
    """
    Copy files to the human review directory.

    Args:
        files: List of file paths to copy.
        source_dir: Source directory.
        dest_dir: Destination directory.
    """
    import shutil

    os.makedirs(dest_dir, exist_ok=True)

    for file_path in files:
        if os.path.exists(file_path):
            dest_path = os.path.join(dest_dir, os.path.basename(file_path))
            shutil.copy(file_path, dest_path)
