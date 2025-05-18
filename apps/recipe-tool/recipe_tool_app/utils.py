"""Utility functions for the Recipe Tool app."""

import logging
import os
import time
from typing import Any, Dict, Optional, Tuple

from recipe_executor.context import Context


def get_repo_root() -> str:
    """Get the absolute path to the repository root."""
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
    logger = logging.getLogger(__name__)
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

    # Return the originally resolved path
    return resolved_path


def prepare_context(context_vars: Optional[str] = None) -> Tuple[Dict[str, Any], Context]:
    """Prepare recipe context from context variables string.

    Args:
        context_vars: Optional string of context variables in format "key1=value1,key2=value2"

    Returns:
        tuple: (context_dict, Context object)
    """
    logger = logging.getLogger(__name__)

    # Start with empty dictionary
    context_dict = {}

    # Set up default paths
    repo_root = get_repo_root()
    default_paths = {
        "recipe_root": os.path.join(repo_root, "recipes"),
        "ai_context_root": os.path.join(repo_root, "ai_context"),
        "output_root": os.path.join(repo_root, "output"),
    }

    # Add default paths first
    context_dict.update(default_paths)

    # Parse user-provided context variables (these will override defaults)
    if context_vars:
        logger.debug(f"Parsing context variables: {context_vars}")
        for item in context_vars.split(","):
            if "=" in item:
                key, value = item.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Log if we're overriding a default path
                if key in default_paths:
                    logger.debug(f"Overriding default path {key}: {default_paths[key]} -> {value}")

                context_dict[key] = value

    # Ensure output directory exists
    os.makedirs(context_dict["output_root"], exist_ok=True)

    # Log all context variables for debugging
    logger.debug(f"Final context variables: {context_dict}")

    return context_dict, Context(artifacts=context_dict)


def extract_recipe_content(generated_recipe: Any) -> Optional[str]:
    """Extract recipe content from various formats.

    Args:
        generated_recipe: Recipe in any supported format

    Returns:
        str: Recipe content if found, None otherwise
    """
    if isinstance(generated_recipe, str):
        return generated_recipe

    if isinstance(generated_recipe, list) and generated_recipe:
        item = generated_recipe[0]
        if isinstance(item, dict) and "content" in item:
            return item["content"]

    if isinstance(generated_recipe, dict) and "content" in generated_recipe:
        return generated_recipe["content"]

    return None


def find_recent_json_file(directory: str, max_age_seconds: int = 30) -> Tuple[Optional[str], Optional[str]]:
    """Find the most recently modified JSON file in a directory.

    Args:
        directory: Directory to search in
        max_age_seconds: Maximum age of file in seconds

    Returns:
        tuple: (file_content, file_path) if found, (None, None) otherwise
    """
    logger = logging.getLogger(__name__)

    if not os.path.exists(directory):
        logger.warning(f"Directory not found: {directory}")
        return None, None

    try:
        # Find all JSON files
        json_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".json")]

        if not json_files:
            logger.warning(f"No JSON files found in {directory}")
            return None, None

        # Get the newest file
        newest_file = max(json_files, key=os.path.getmtime)
        file_age = time.time() - os.path.getmtime(newest_file)

        # Check if it's recent enough
        if file_age > max_age_seconds:
            logger.warning(f"Most recent JSON file {newest_file} is {file_age:.2f} seconds old, skipping")
            return None, None

        # Read the file
        logger.info(f"Found recent JSON file: {newest_file}")
        with open(newest_file, "r") as f:
            content = f.read()
            logger.info(f"Read content from {newest_file}")
            return content, newest_file

    except Exception as e:
        logger.warning(f"Error while searching for recent files: {e}")
        return None, None


def parse_recipe_json(recipe_content: str) -> Dict[str, Any]:
    """Parse recipe JSON and provide a structured preview.

    Args:
        recipe_content: Recipe JSON as string

    Returns:
        dict: Parsed recipe JSON
    """
    import json

    if not recipe_content:
        return {}

    # Make sure it's a string
    if not isinstance(recipe_content, str):
        if isinstance(recipe_content, (dict, list)):
            recipe_content = json.dumps(recipe_content, indent=2)
        else:
            recipe_content = str(recipe_content)

    # Parse JSON
    return json.loads(recipe_content)


def handle_recipe_error(func):
    """Decorator to standardize error handling for recipe operations."""
    import asyncio
    import functools
    import logging

    logger = logging.getLogger(__name__)

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}", exc_info=True)
            error_msg = f"### Error\n\n```\n{str(e)}\n```"

            # Use appropriate result format based on function name
            if "execute" in func.__name__:
                return {"formatted_results": error_msg, "raw_json": "{}", "debug_context": {"error": str(e)}}
            else:
                return {"recipe_json": "", "structure_preview": error_msg, "debug_context": {"error": str(e)}}

    # Handle non-async functions
    if not asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(wrapper(*args, **kwargs))

        return sync_wrapper

    return wrapper
