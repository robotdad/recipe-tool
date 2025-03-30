import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Union

from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY


class RecipeExecutor:
    """
    RecipeExecutor is the central orchestration mechanism for the Recipe Executor system.
    It loads and executes recipes from various input formats sequentially using a provided context.
    """

    def __init__(self) -> None:
        # Stateless design; no initialization required
        pass

    def execute(
        self,
        recipe: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        context: Context,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Execute a recipe with the provided context.

        Args:
            recipe: Recipe to execute. It can be a file path, a JSON string, a dict, or a list of step dicts.
            context: Context instance to use for execution.
            logger: Optional logger to use, defaults to a simple console logger if not provided.

        Raises:
            ValueError: If the recipe format is invalid or a step execution fails.
            TypeError: If the recipe type is not supported.
        """
        if logger is None:
            logger = logging.getLogger(__name__)
            if not logger.handlers:
                # Set up a basic console handler if no handlers exist
                handler = logging.StreamHandler()
                formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        try:
            # Parse the recipe based on its type
            recipe_data = self._load_recipe(recipe, logger)
        except Exception as e:
            msg = f"Failed to load recipe: {str(e)}"
            logger.error(msg)
            raise ValueError(msg) from e

        # Validate recipe structure - expecting either a dict with a 'steps' key or a list of steps
        steps = []
        if isinstance(recipe_data, dict):
            if "steps" not in recipe_data:
                msg = "Recipe dictionary must have a 'steps' key."
                logger.error(msg)
                raise ValueError(msg)
            steps = recipe_data["steps"]
        elif isinstance(recipe_data, list):
            steps = recipe_data
        else:
            msg = f"Unsupported recipe format: {type(recipe_data)}."
            logger.error(msg)
            raise TypeError(msg)

        if not isinstance(steps, list):
            msg = "'steps' should be a list of step definitions."
            logger.error(msg)
            raise ValueError(msg)

        logger.info(f"Executing recipe with {len(steps)} steps.")

        # Execute each step sequentially
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                msg = f"Step at index {index} is not a dictionary."
                logger.error(msg)
                raise ValueError(msg)

            if "type" not in step:
                msg = f"Step at index {index} is missing the 'type' field."
                logger.error(msg)
                raise ValueError(msg)

            step_type = step["type"]
            if step_type not in STEP_REGISTRY:
                msg = f"Unknown step type '{step_type}' at index {index}."
                logger.error(msg)
                raise ValueError(msg)

            step_class = STEP_REGISTRY[step_type]
            try:
                logger.info(f"Executing step {index + 1}/{len(steps)}: {step_type}")
                step_instance = step_class(step, logger)
                step_instance.execute(context)
            except Exception as e:
                msg = f"Error executing step {index} (type: {step_type}): {str(e)}"
                logger.error(msg)
                raise ValueError(msg) from e

        logger.info("Recipe execution completed successfully.")

    def _load_recipe(
        self, recipe: Union[str, Dict[str, Any], List[Dict[str, Any]]], logger: logging.Logger
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Load and parse the recipe from various formats:

        - If recipe is a path to a file, load its content.
        - If the file is markdown, extract JSON from fenced code blocks.
        - If recipe is a JSON string, parse it.
        - If recipe is already a dict or list, return it directly.
        """
        logger.info(f"Loading recipe from: {recipe}")

        # If recipe is a dict or list, return it directly
        if isinstance(recipe, (dict, list)):
            return recipe

        if isinstance(recipe, str):
            # If the string is a path to an existing file, load file content
            if os.path.exists(recipe) and os.path.isfile(recipe):
                try:
                    with open(recipe, "r", encoding="utf-8") as file:
                        content = file.read()
                        logger.info(f"Loaded recipe from file: {recipe}")
                except Exception as e:
                    raise ValueError(f"Failed to read recipe file '{recipe}': {str(e)}") from e

                # Check if it's a markdown file by extension
                if recipe.lower().endswith(".md"):
                    # Extract JSON from markdown fenced code blocks
                    json_content = self._extract_json_from_markdown(content)
                    if json_content is None:
                        raise ValueError("No JSON code block found in markdown recipe.")
                    content = json_content

                # Parse the content as JSON
                try:
                    return json.loads(content)
                except Exception as e:
                    raise ValueError(f"Invalid JSON in recipe file '{recipe}': {str(e)}") from e
            else:
                # Try to parse the string directly as JSON
                try:
                    return json.loads(recipe)
                except Exception as e:
                    raise ValueError(f"Invalid recipe format string: {str(e)}") from e

        # Unsupported recipe type
        raise TypeError(f"Recipe type {type(recipe)} is not supported.")

    def _extract_json_from_markdown(self, content: str) -> Optional[str]:
        """
        Extract the first JSON fenced code block from a markdown string.

        Returns:
            The JSON string if found, otherwise None.
        """
        # Regex to match fenced code block with json language indicator
        pattern = r"```json\s*(.*?)\s*```"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
