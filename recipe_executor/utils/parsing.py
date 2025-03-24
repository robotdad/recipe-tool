"""Recipe parsing utilities for Recipe Executor."""

import json
import logging
import re
from typing import Any, Dict, Union

import yaml

from recipe_executor.models.recipe import Recipe

logger = logging.getLogger("recipe-executor")


def parse_natural_language_recipe(
    nl_content: str,
    model_provider: str = "anthropic",
    model_name: str = "claude-3-7-sonnet-20250219",
    temperature: float = 0.1,
) -> Recipe:
    """
    Parse a natural language recipe into a structured recipe using an LLM.

    Args:
        nl_content: Natural language recipe content
        model_provider: Provider of the LLM
        model_name: Name of the LLM model
        temperature: Temperature for LLM generation

    Returns:
        Structured recipe
    """
    raise NotImplementedError(
        "This function must be implemented by the main executor class"
    )


def extract_structured_from_markdown(markdown_content: str) -> Dict[str, Any]:
    """
    Extract structured YAML or JSON content from a markdown file.

    Args:
        markdown_content: Markdown content to extract from

    Returns:
        Dictionary of structured data or empty dict if none found
    """
    # Try to extract YAML
    yaml_match = re.search(r"```ya?ml\s*\n(.*?)\n```", markdown_content, re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)
        try:
            return yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML from markdown: {e}")

    # Try to extract JSON
    json_match = re.search(r"```json\s*\n(.*?)\n```", markdown_content, re.DOTALL)
    if json_match:
        json_content = json_match.group(1)
        try:
            return json.loads(json_content)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from markdown: {e}")

    return {}


def load_recipe_from_file(file_path: str) -> Union[Recipe, Dict[str, Any], str]:
    """
    Load a recipe from a file.

    Args:
        file_path: Path to the recipe file

    Returns:
        Recipe, dict, or string content depending on file type
    """
    with open(file_path, "r") as f:
        content = f.read()

    # Determine file type
    if file_path.endswith(".json"):
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON file: {e}")
            return content
    elif file_path.endswith((".yaml", ".yml")):
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML file: {e}")
            return content
    elif file_path.endswith(".md"):
        structured = extract_structured_from_markdown(content)
        if structured:
            return structured
        return content
    else:
        return content
