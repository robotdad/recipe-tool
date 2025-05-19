"""Example handling functionality for the Recipe Tool app."""

import json
import logging
import os
from typing import Dict, Tuple

from recipe_tool_app.error_handler import handle_recipe_error
from recipe_tool_app.file_operations import read_file
from recipe_tool_app.path_resolver import get_potential_paths, get_repo_root

# Initialize logger
logger = logging.getLogger(__name__)


@handle_recipe_error
async def load_example(example_path: str) -> Dict[str, str]:
    """Load an example recipe from the examples directory.

    Args:
        example_path: Path to the example recipe file

    Returns:
        dict: Contains recipe_content and description keys
    """
    if not example_path:
        return {"recipe_content": "", "description": "No example selected."}

    try:
        # Log the original path for debugging
        logger.info(f"Loading example from path: {example_path}")

        # Try to find the file using potential paths

        # Generate potential paths to try
        potential_paths = get_potential_paths(example_path)

        # Try each path until we find one that exists
        full_path = None
        for path in potential_paths:
            if os.path.exists(path):
                full_path = path
                logger.info(f"Found example at: {full_path}")
                break

        if not full_path:
            # Log all attempted paths for debugging
            logger.error(f"Failed to find example recipe. Tried the following paths: {potential_paths}")
            return {
                "recipe_content": "",
                "description": f"Error: Could not find example recipe. Please check paths: {example_path}",
            }

        # Read the content
        content = read_file(full_path)

        # Try to find README file with description
        dir_path = os.path.dirname(full_path)
        readme_path = os.path.join(dir_path, "README.md")
        desc = ""
        if os.path.exists(readme_path):
            desc = read_file(readme_path)

        return {
            "recipe_content": content,
            "description": desc or "No description available for this example.",
        }
    except Exception as e:
        logger.error(f"Error loading example: {e}")
        return {"recipe_content": "", "description": f"Error loading example: {str(e)}"}


async def load_example_formatted(path: str) -> Tuple[str, str]:
    """Load an example recipe and format for UI.

    Args:
        path: Path to the example recipe

    Returns:
        Tuple[str, str]: (recipe_content, description)
    """
    result = await load_example(path)
    # Ensure we return strings even if result contains None values
    return result.get("recipe_content", ""), result.get("description", "")


def find_examples_in_directory(directory: str) -> Dict[str, str]:
    """Find all JSON recipe examples in a directory.

    Args:
        directory: Directory to search in

    Returns:
        Dict[str, str]: Map of display names to file paths
    """
    if not os.path.exists(directory) or not os.path.isdir(directory):
        logger.warning(f"Example directory not found: {directory}")
        return {}

    examples = {}
    repo_root = get_repo_root()

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, repo_root)

                # Try to read the file to extract name if it's a recipe
                try:
                    # Read and parse the file content as JSON
                    content = json.loads(read_file(full_path))
                    name = content.get("name", file)
                    examples[f"{name} ({rel_path})"] = full_path
                except Exception as e:
                    # If we can't parse it as JSON, just use the filename
                    logger.debug(f"Could not parse {full_path} as JSON: {e}")
                    examples[f"{file} ({rel_path})"] = full_path

    return examples
