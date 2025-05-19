"""Recipe processing utilities for the Recipe Tool app."""

import json
import logging
from typing import Any, Dict, Optional, Tuple

# Initialize logger
logger = logging.getLogger(__name__)


def parse_recipe_json(recipe_content: str) -> Dict[str, Any]:
    """Parse recipe JSON and return a structured dictionary.

    Args:
        recipe_content: Recipe JSON as string

    Returns:
        dict: Parsed recipe JSON
    """
    logger.debug("Parsing recipe JSON")

    if not recipe_content:
        logger.warning("Empty recipe content")
        return {}

    # Make sure it's a string
    if not isinstance(recipe_content, str):
        if isinstance(recipe_content, (dict, list)):
            recipe_content = json.dumps(recipe_content, indent=2)
            logger.debug("Converted dict/list to JSON string")
        else:
            recipe_content = str(recipe_content)
            logger.debug("Converted non-string content to string")

    # Parse JSON
    try:
        parsed = json.loads(recipe_content)
        logger.debug("Successfully parsed recipe JSON")
        return parsed
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing recipe JSON: {e}")
        # Return empty dict on error
        return {}


def extract_recipe_content(generated_recipe: Any) -> Optional[str]:
    """Extract recipe content from various formats.

    Args:
        generated_recipe: Recipe in any supported format

    Returns:
        str: Recipe content if found, None otherwise
    """
    logger.debug(f"Extracting recipe content from {type(generated_recipe)}")

    if isinstance(generated_recipe, str):
        logger.debug("Recipe is already a string")
        return generated_recipe

    if isinstance(generated_recipe, list) and generated_recipe:
        item = generated_recipe[0]
        if isinstance(item, dict) and "content" in item:
            logger.debug("Extracted content from first item in list")
            return item["content"]

    if isinstance(generated_recipe, dict) and "content" in generated_recipe:
        logger.debug("Extracted content from dictionary")
        return generated_recipe["content"]

    logger.warning("Could not extract recipe content")
    return None


def generate_recipe_preview(recipe_json: Dict[str, Any], execution_time: float = 0.0) -> str:
    """Generate a markdown preview of a recipe structure.

    Args:
        recipe_json: Parsed recipe JSON
        execution_time: Optional execution time to include in the preview

    Returns:
        str: Markdown formatted preview
    """
    logger.debug("Generating recipe preview")

    # Create a markdown preview of the recipe structure
    preview = "### Recipe Structure\n\n"

    if execution_time > 0:
        preview += f"**Execution Time**: {execution_time:.2f} seconds\n\n"

    if "name" in recipe_json:
        preview += f"**Name**: {recipe_json['name']}\n\n"

    if "description" in recipe_json:
        preview += f"**Description**: {recipe_json['description']}\n\n"

    if "steps" in recipe_json and isinstance(recipe_json["steps"], list):
        preview += f"**Steps**: {len(recipe_json['steps'])}\n\n"
        preview += "| # | Type | Description |\n"
        preview += "|---|------|-------------|\n"

        for i, step in enumerate(recipe_json["steps"]):
            step_type = step.get("type", "unknown")
            step_desc = ""

            if "config" in step and "description" in step["config"]:
                step_desc = step["config"]["description"]
            elif "description" in step:
                step_desc = step["description"]

            preview += f"| {i + 1} | {step_type} | {step_desc} |\n"

    logger.debug("Recipe preview generated successfully")
    return preview


def validate_recipe(recipe_json: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate a recipe JSON structure and return (is_valid, error_message).

    Args:
        recipe_json: Recipe JSON dictionary

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    logger.debug("Validating recipe")

    # Check for required fields
    if not recipe_json:
        return False, "Recipe is empty"

    if "steps" not in recipe_json:
        return False, "Recipe must contain 'steps' field"

    if not isinstance(recipe_json["steps"], list):
        return False, "'steps' field must be a list"

    # Validate each step
    for i, step in enumerate(recipe_json["steps"]):
        if not isinstance(step, dict):
            return False, f"Step {i + 1} must be a dictionary"

        if "type" not in step:
            return False, f"Step {i + 1} is missing required 'type' field"

    logger.debug("Recipe validation successful")
    return True, None


def format_recipe_results(results: Dict[str, Any], execution_time: float = 0.0) -> str:
    """Format recipe execution results as markdown.

    Args:
        results: Dictionary containing result data
        execution_time: Execution time in seconds

    Returns:
        str: Markdown formatted results
    """
    logger.debug("Formatting recipe results")

    if results:
        markdown_output = "### Recipe Execution Successful\n\n"

        if execution_time > 0:
            markdown_output += f"**Execution Time**: {execution_time:.2f} seconds\n\n"

        markdown_output += "#### Results\n\n"

        for key, value in results.items():
            markdown_output += f"**{key}**:\n"
            # Check if value is JSON
            try:
                if isinstance(value, str):
                    json_obj = json.loads(value)
                    markdown_output += f"```json\n{json.dumps(json_obj, indent=2)}\n```\n\n"
                else:
                    # Already a dict or list
                    markdown_output += f"```json\n{json.dumps(value, indent=2)}\n```\n\n"
            except (json.JSONDecodeError, TypeError):
                # Not JSON, treat as regular text
                markdown_output += f"```\n{value}\n```\n\n"
    else:
        markdown_output = "### Recipe Execution Successful\n\n"

        if execution_time > 0:
            markdown_output += f"**Execution Time**: {execution_time:.2f} seconds\n\n"

        markdown_output += "No string results were found in the context."

    logger.debug("Recipe results formatted successfully")
    return markdown_output


def extract_results_from_context(context: Dict[str, Any]) -> Dict[str, str]:
    """Extract only the result/output entries from a context dictionary.

    Args:
        context: The full context dictionary

    Returns:
        Dict[str, str]: Dictionary containing only the results
    """
    logger.debug("Extracting results from context")

    results = {}
    for key, value in context.items():
        # Only include string results or keys that look like outputs
        if isinstance(value, str) and (key.startswith("output") or key.startswith("result")):
            results[key] = value

    logger.debug(f"Extracted {len(results)} results from context")
    return results


def format_context_for_display(context: Dict[str, Any]) -> str:
    """Format the context dictionary for display as JSON.

    Args:
        context: Context dictionary

    Returns:
        str: JSON formatted context
    """
    logger.debug("Formatting context for display")

    try:
        # Format raw JSON output using a simple default function to handle non-serializable types
        return json.dumps(context, indent=2, default=lambda o: str(o))
    except Exception as e:
        logger.error(f"Error formatting context: {e}")
        return "{}"
