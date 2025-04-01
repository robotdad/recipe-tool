import os
import json
import re
import logging
from typing import Any, Dict, Union, Optional

from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY

class RecipeExecutor:
    def __init__(self) -> None:
        # Nothing to init for now
        pass

    def execute(
        self,
        recipe: Union[str, Dict[str, Any]],
        context: Context,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """
        Execute a recipe with the given context.

        Args:
            recipe: Recipe to execute, can be a file path, JSON string, or dictionary
            context: Context instance to use for execution
            logger: Optional logger to use, creates a default one if not provided

        Raises:
            ValueError: If recipe format is invalid or step execution fails
            TypeError: If recipe type is not supported
        """
        if logger is None:
            logger = logging.getLogger(__name__)
            if not logger.hasHandlers():
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)

        try:
            recipe_dict = self._load_and_parse_recipe(recipe, logger)
        except Exception as e:
            raise ValueError(f"Failed to load and parse recipe: {str(e)}") from e

        # Validate recipe structure
        if "steps" not in recipe_dict or not isinstance(recipe_dict["steps"], list):
            raise ValueError("Invalid recipe format: 'steps' key missing or not a list")

        steps = recipe_dict["steps"]
        logger.debug(f"Executing {len(steps)} step(s) from recipe")

        # Execute each step in sequence
        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                raise ValueError(f"Step at index {idx} is not a valid dict")
            if "type" not in step:
                raise ValueError(f"Step at index {idx} missing required 'type' field")

            step_type = step["type"]
            if step_type not in STEP_REGISTRY:
                raise ValueError(f"Unknown step type '{step_type}' at index {idx}")

            step_class = STEP_REGISTRY[step_type]
            try:
                logger.debug(f"Executing step {idx} of type '{step_type}'")
                step_instance = step_class(step, logger)
                step_instance.execute(context)
            except Exception as e:
                # Provide detailed error message including step index and original error
                raise ValueError(f"Error executing step {idx} of type '{step_type}': {str(e)}") from e

    def _load_and_parse_recipe(
        self,
        recipe_input: Union[str, Dict[str, Any]],
        logger: logging.Logger
    ) -> Dict[str, Any]:
        """
        Load and parse the recipe from supported formats.

        Args:
            recipe_input: File path, JSON string, or dictionary representing a recipe
            logger: Logger for debug messages

        Returns:
            A dictionary representing the recipe

        Raises:
            ValueError: if the recipe cannot be parsed
            TypeError: if the recipe_input type is unsupported
        """
        if isinstance(recipe_input, dict):
            logger.debug("Recipe input provided as a dictionary")
            return recipe_input
        elif isinstance(recipe_input, str):
            # Check if it's a file path
            if os.path.exists(recipe_input):
                logger.debug(f"Loading recipe from file: {recipe_input}")
                try:
                    with open(recipe_input, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    raise ValueError(f"Error reading recipe file '{recipe_input}': {str(e)}") from e
            else:
                logger.debug("Recipe input provided as a JSON string")
                content = recipe_input

            # Attempt to extract JSON from markdown fenced code blocks
            content = self._extract_json_from_markdown(content, logger)

            try:
                recipe_dict = json.loads(content)
            except Exception as e:
                raise ValueError(f"Invalid JSON format in recipe: {str(e)}") from e
            return recipe_dict
        else:
            raise TypeError(f"Unsupported recipe type: {type(recipe_input)}")

    def _extract_json_from_markdown(self, content: str, logger: logging.Logger) -> str:
        """
        Extract JSON content from a markdown fenced code block if present.

        Args:
            content: Input string that might contain Markdown code fences
            logger: Logger for debug messages

        Returns:
            JSON string extracted from the fenced code block, or the original content if not found
        """
        # Look for a fenced code block with json
        pattern = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)
        match = pattern.search(content)
        if match:
            logger.debug("Extracted JSON from markdown code fence")
            return match.group(1)
        else:
            logger.debug("No markdown code fence found, using raw content")
            return content
