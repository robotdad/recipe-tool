"""Path resolution utilities for Recipe Tool.

This module handles all path-related operations including finding recipe roots,
output directories, and resolving file paths.
"""

import os
from typing import Dict, Optional


def get_recipe_paths() -> Dict[str, str]:
    """Get common recipe-related paths.

    Returns:
        Dictionary with recipe_root, ai_context_root, and output_root paths.
    """
    from recipe_executor_app.utils import get_repo_root, get_main_repo_root

    # Get the current app's repo root
    app_root = get_repo_root()
    main_repo_root = get_main_repo_root()

    # Fallback to app root if not found
    if not main_repo_root:
        main_repo_root = app_root

    return {
        "recipe_root": os.path.join(main_repo_root, "recipes"),
        "ai_context_root": os.path.join(main_repo_root, "ai_context"),
        "output_root": os.path.join(app_root, "output"),
    }


def prepare_context_paths(context_dict: Dict[str, str]) -> Dict[str, str]:
    """Add default paths to context dictionary if not present.

    Args:
        context_dict: Context dictionary to update

    Returns:
        Updated context dictionary with default paths
    """
    paths = get_recipe_paths()

    # Add defaults if not present
    for key, value in paths.items():
        context_dict.setdefault(key, value)

    # Ensure output directory exists
    os.makedirs(context_dict["output_root"], exist_ok=True)

    return context_dict


def find_recipe_creator() -> Optional[str]:
    """Find the recipe creator path.

    Returns:
        Path to recipe creator or None if not found
    """
    paths = get_recipe_paths()
    creator_path = os.path.join(paths["recipe_root"], "recipe_creator/create.json")

    return creator_path if os.path.exists(creator_path) else None


def resolve_output_path(output_root: str, target_file: str) -> str:
    """Resolve the full path for an output file.

    Args:
        output_root: Root output directory
        target_file: Target filename (can be relative or absolute)

    Returns:
        Resolved absolute path
    """
    if os.path.isabs(target_file):
        return target_file
    return os.path.join(output_root, target_file)
