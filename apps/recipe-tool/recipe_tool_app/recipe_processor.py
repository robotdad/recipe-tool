"""Recipe processing utilities for Recipe Tool.

This module handles recipe output finding, parsing, and preview generation.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

from recipe_executor_app.utils import read_file

from .path_resolver import resolve_output_path


logger = logging.getLogger(__name__)


def find_recipe_output(context_dict: Dict[str, Any]) -> Optional[str]:
    """Find the recipe output from context or files.

    Args:
        context_dict: Context dictionary from recipe execution

    Returns:
        Recipe JSON content or None if not found
    """
    # Check context first
    if "generated_recipe" in context_dict:
        content = context_dict["generated_recipe"]
        if isinstance(content, str):
            return content
        elif isinstance(content, list) and content:
            if isinstance(content[0], dict) and "content" in content[0]:
                return content[0]["content"]
        elif isinstance(content, dict) and "content" in content:
            return content["content"]

    # Check output file
    output_root = context_dict.get("output_root", "output")
    target_file = context_dict.get("target_file", "generated_recipe.json")
    file_path = resolve_output_path(output_root, target_file)

    if os.path.exists(file_path):
        try:
            return read_file(file_path)
        except Exception as e:
            logger.warning(f"Failed to read {file_path}: {e}")

    # Check for recent JSON files
    if os.path.exists(output_root):
        import time

        current_time = time.time()
        for file in sorted(os.listdir(output_root), reverse=True):
            if file.endswith(".json"):
                try:
                    path = os.path.join(output_root, file)
                    # Check if file was created recently (within last 30 seconds)
                    if os.path.getmtime(path) > current_time - 30:
                        return read_file(path)
                except Exception:
                    continue

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
