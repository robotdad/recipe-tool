import os
import json
import logging
from typing import Any, Dict, Union, Optional

from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY

class RecipeExecutor:
    """
    The RecipeExecutor is responsible for orchestrating the execution of a recipe.
    It supports loading recipes from file paths, JSON strings, or dictionaries, validates
    the recipe structure, and executes each step sequentially using the provided context.
    """

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
            if not logger.handlers:
                # Create a basic configuration if none exists
                logging.basicConfig(level=logging.DEBUG)

        logger.debug("Starting recipe execution.")

        # Load and parse recipe into a dictionary
        recipe_payload: Dict[str, Any]
        if isinstance(recipe, dict):
            recipe_payload = recipe
            logger.debug("Recipe provided as dictionary.")
        elif isinstance(recipe, str):
            # Check if it's a file path
            if os.path.exists(recipe):
                logger.debug(f"Loading recipe from file: {recipe}")
                try:
                    with open(recipe, 'r', encoding='utf-8') as file:
                        recipe_payload = json.load(file)
                except Exception as e:
                    raise ValueError(f"Failed to load recipe from file '{recipe}': {e}")
            else:
                # Assume it's a JSON string
                logger.debug("Loading recipe from JSON string.")
                try:
                    recipe_payload = json.loads(recipe)
                except Exception as e:
                    raise ValueError(f"Failed to parse recipe JSON string: {e}")
        else:
            raise TypeError("Unsupported recipe type. Must be a file path, JSON string, or dictionary.")

        logger.debug(f"Parsed recipe payload: {recipe_payload}")

        # Validate that the recipe contains a 'steps' key
        if 'steps' not in recipe_payload or not isinstance(recipe_payload['steps'], list):
            raise ValueError("Invalid recipe format: Missing 'steps' list.")

        steps = recipe_payload['steps']

        # Execute steps sequentially
        for index, step in enumerate(steps):
            logger.debug(f"Processing step {index + 1}: {step}")

            if not isinstance(step, dict):
                raise ValueError(f"Invalid step format at index {index}: Step must be a dictionary.")

            if 'type' not in step:
                raise ValueError(f"Missing 'type' in step at index {index}.")

            step_type = step['type']
            if step_type not in STEP_REGISTRY:
                raise ValueError(f"Unknown step type '{step_type}' at index {index}.")

            step_class = STEP_REGISTRY[step_type]

            try:
                # Instantiate the step with its definition and logger
                step_instance = step_class(step, logger)
                logger.debug(f"Executing step {index + 1} of type '{step_type}'.")
                step_instance.execute(context)
                logger.debug(f"Completed step {index + 1}.")
            except Exception as e:
                # Wrap and re-raise with step index for clarity
                raise ValueError(f"Error executing step {index + 1} (type: '{step_type}'): {e}") from e

        logger.debug("Recipe execution completed successfully.")
