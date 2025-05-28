"""Recipe processing utilities for Recipe Tool.

This module handles recipe output finding, parsing, and preview generation.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

from recipe_executor_app.utils import read_file


logger = logging.getLogger(__name__)


def find_recipe_output(context_dict: Dict[str, Any]) -> Optional[str]:
    """Find the recipe output from the generated file.

    Args:
        context_dict: Context dictionary from recipe execution

    Returns:
        Recipe JSON content or None if not found
    """
    # Get the generated recipe path from context
    if "generated_recipe" not in context_dict:
        logger.error("No generated_recipe in context")
        return None

    generated_recipe = context_dict["generated_recipe"]
    if not isinstance(generated_recipe, list) or not generated_recipe:
        logger.error(f"generated_recipe is not a list or is empty: {type(generated_recipe)}")
        return None

    # Get the first generated recipe file (FileSpec object)
    first_recipe = generated_recipe[0]

    # Extract path from FileSpec object
    if not hasattr(first_recipe, "path"):
        logger.error(f"Recipe item doesn't have path attribute: {type(first_recipe)}")
        return None

    recipe_filename = first_recipe.path

    # Build the full path
    output_root = context_dict.get("output_root", "output")
    file_path = os.path.join(output_root, recipe_filename)

    # Read the file
    try:
        content = read_file(file_path)
        logger.info(f"Successfully read generated recipe from: {file_path}")
        return content
    except Exception as e:
        logger.error(f"Failed to read generated recipe from {file_path}: {e}")
        return None


def generate_preview(recipe: Dict[str, Any], execution_time: float) -> str:
    """Generate a markdown preview of the recipe.

    Args:
        recipe: Parsed recipe dictionary
        execution_time: Time taken to execute recipe

    Returns:
        Markdown formatted preview string
    """
    preview = "### Recipe Structure\n\n"
    preview += f"**Execution Time**: {execution_time:.2f} seconds\n\n"

    if "name" in recipe:
        preview += f"**Name**: {recipe['name']}\n\n"

    if "description" in recipe:
        preview += f"**Description**: {recipe['description']}\n\n"

    if "steps" in recipe and isinstance(recipe["steps"], list):
        preview += f"**Steps**: {len(recipe['steps'])}\n\n"
        preview += "| # | Type | Description |\n"
        preview += "|---|------|-------------|\n"

        for i, step in enumerate(recipe["steps"]):
            step_type = step.get("type", "unknown")
            desc = step.get("config", {}).get("description", step.get("description", ""))
            preview += f"| {i + 1} | {step_type} | {desc} |\n"

    return preview


def process_recipe_output(output_recipe: str, execution_time: float, context_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Process recipe output and generate result dictionary.

    Args:
        output_recipe: Recipe JSON string
        execution_time: Time taken to execute
        context_dict: Final context dictionary

    Returns:
        Result dictionary with recipe_json, structure_preview, and debug_context
    """
    try:
        recipe = json.loads(output_recipe)
        preview = generate_preview(recipe, execution_time)

        return {
            "recipe_json": output_recipe,
            "structure_preview": preview,
            "debug_context": context_dict,
        }
    except json.JSONDecodeError:
        return {
            "recipe_json": output_recipe,
            "structure_preview": f"### Recipe Created\n\n**Time**: {execution_time:.2f}s\n\nWarning: Invalid JSON",
            "debug_context": context_dict,
        }
