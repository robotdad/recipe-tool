"""Path resolution utilities for the Recipe Tool app."""

import logging
import os
from typing import List, Optional

# Initialize logger
logger = logging.getLogger(__name__)


def get_repo_root() -> str:
    """Get the absolute path to the repository root.

    Returns:
        str: Absolute path to the repository root directory
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def resolve_path(path: str, root: Optional[str] = None, attempt_fixes: bool = True) -> str:
    """Resolve a path to an absolute path, optionally relative to a root.

    Args:
        path: The path to resolve
        root: Optional root directory to resolve relative paths against
        attempt_fixes: Whether to attempt to fix common path resolution issues

    Returns:
        str: The absolute path
    """
    logger.debug(f"Resolving path: '{path}' (root: '{root}')")

    # Get repo root for reference
    repo_root = get_repo_root()
    logger.debug(f"Repository root: {repo_root}")

    # First, check if it's already an absolute path
    if os.path.isabs(path):
        logger.debug(f"Path is already absolute: {path}")
        return path

    # Normal case: relative to specified root or repo root
    resolved_path = None

    # Handle paths that are relative to repo root with ../ prefix
    if path.startswith("../") or path.startswith("../../"):
        # Start from repo root and navigate up as needed
        current_path = repo_root
        parts = path.split("/")

        # Count initial "../" parts to determine how many levels up to go
        up_levels = 0
        for part in parts:
            if part == "..":
                up_levels += 1
            else:
                break

        # Go up the required number of levels from repo root
        for _ in range(up_levels):
            current_path = os.path.dirname(current_path)

        # Join with the remainder of the path (excluding the "../" parts)
        resolved_path = os.path.join(current_path, *parts[up_levels:])
        logger.debug(f"Resolved ../ path to: {resolved_path}")
    elif root:
        # Relative to specified root
        if not os.path.isabs(root):
            root = os.path.join(repo_root, root)
        resolved_path = os.path.join(root, path)
        logger.debug(f"Resolved path relative to root: {resolved_path}")
    else:
        # Default: relative to repo root
        resolved_path = os.path.join(repo_root, path)
        logger.debug(f"Resolved path relative to repo root: {resolved_path}")

    # Check if the resolved path exists and attempt fixes if not
    if attempt_fixes and not os.path.exists(resolved_path):
        logger.debug(f"Resolved path does not exist, attempting fixes: {resolved_path}")

        # Try to fix using various strategies
        alt_path = _attempt_path_fixes(path, repo_root)
        if alt_path:
            return alt_path

    # Return the originally resolved path
    return resolved_path


def _attempt_path_fixes(path: str, repo_root: str) -> Optional[str]:
    """Attempt various fixes for a path that doesn't exist.

    Args:
        path: The original path string
        repo_root: The repository root path

    Returns:
        Optional[str]: Fixed path if successful, None otherwise
    """
    # Prepare potential alternatives
    alternatives = []

    # If path contains "recipes", try to resolve relative to the recipes directory
    if "recipes" in path:
        recipes_dir = os.path.join(repo_root, "recipes")

        # Get the part after "recipes/"
        if "recipes/" in path:
            after_recipes = path.split("recipes/", 1)[1]
            alternatives.append(os.path.join(recipes_dir, after_recipes))
            logger.debug(f"Added alternative from recipes/ split: {alternatives[-1]}")

        # Try with just the basename
        basename = os.path.basename(path)

        # Try finding the file recursively in the recipes directory
        for root, _, files in os.walk(recipes_dir):
            if basename in files:
                alternatives.append(os.path.join(root, basename))
                logger.debug(f"Found file by basename in recipes dir: {alternatives[-1]}")

    # If nothing found, try some common paths
    if not alternatives:
        # Try joining with recipes directory
        alternatives.append(os.path.join(repo_root, "recipes", path))
        logger.debug(f"Added recipes fallback: {alternatives[-1]}")

        # Try joining with recipe-tool directory
        alternatives.append(os.path.join(repo_root, "apps", "recipe-tool", path))
        logger.debug(f"Added recipe-tool fallback: {alternatives[-1]}")

    # Check alternatives
    for alt_path in alternatives:
        if os.path.exists(alt_path):
            logger.debug(f"Found existing alternative path: {alt_path}")
            return alt_path

    return None


def find_file_by_name(filename: str, search_dir: str, recursive: bool = True) -> Optional[str]:
    """Find a file by name in a directory, with optional recursive search.

    Args:
        filename: The filename to search for
        search_dir: The directory to search in
        recursive: Whether to search recursively

    Returns:
        Optional[str]: Full path to the file if found, None otherwise
    """
    logger.debug(f"Searching for file: {filename} in {search_dir}")

    if not os.path.exists(search_dir):
        logger.warning(f"Search directory does not exist: {search_dir}")
        return None

    if recursive:
        for root, _, files in os.walk(search_dir):
            if filename in files:
                file_path = os.path.join(root, filename)
                logger.debug(f"Found file: {file_path}")
                return file_path
    else:
        file_path = os.path.join(search_dir, filename)
        if os.path.exists(file_path):
            logger.debug(f"Found file: {file_path}")
            return file_path

    logger.debug(f"File not found: {filename}")
    return None


def ensure_directory_exists(path: str) -> str:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Path to the directory

    Returns:
        str: Path to the directory
    """
    if not os.path.exists(path):
        logger.debug(f"Creating directory: {path}")
        os.makedirs(path, exist_ok=True)
    return path


def get_recipes_directory() -> str:
    """Get the path to the recipes directory.

    Returns:
        str: Path to the recipes directory
    """
    return os.path.join(get_repo_root(), "recipes")


def get_output_directory() -> str:
    """Get the path to the output directory.

    Returns:
        str: Path to the output directory
    """
    output_dir = os.path.join(get_repo_root(), "output")
    return ensure_directory_exists(output_dir)


def get_potential_paths(path: str) -> List[str]:
    """Generate a list of potential paths to try for a given path.

    Args:
        path: The original path

    Returns:
        List[str]: List of potential paths to try
    """
    repo_root = get_repo_root()
    recipe_root = os.path.join(repo_root, "recipes")

    return [
        # 1. Direct interpretation of the path
        path,
        # 2. Relative to repo root
        os.path.join(repo_root, path.lstrip("/")),
        # 3. Relative to recipe_root (replacing initial ../../recipes with recipe_root)
        os.path.join(recipe_root, path.replace("../../recipes/", "")),
        # 4. Relative to recipe_root (replacing initial ../../../recipes with recipe_root)
        os.path.join(recipe_root, path.replace("../../../recipes/", "")),
        # 5. Direct path in recipes directory
        os.path.join(recipe_root, os.path.basename(path)),
    ]
