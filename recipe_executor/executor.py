import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Union

from recipe_executor.steps.registry import STEP_REGISTRY


def extract_json_from_markdown(content: str) -> Optional[str]:
    """
    Extracts JSON content from a markdown fenced code block.

    Args:
        content: The string content possibly containing a fenced code block with JSON.

    Returns:
        The JSON string if a fenced code block is found, otherwise None.
    """
    pattern = re.compile(r"```json\s*(.*?)\s*```", re.DOTALL)
    match = pattern.search(content)
    if match:
        return match.group(1)
    return None


class RecipeExecutor:
    """
    Unified executor that loads a recipe (from a file path, JSON string, or dict),
    and executes its steps sequentially using the provided context.
    """

    def execute(
        self,
        recipe: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        context: Any,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Execute a recipe with the given context.

        Args:
            recipe: Recipe to execute, can be a file path, JSON string, or dict
            context: Context instance to use for execution
            logger: Optional logger to use, creates a default one if not provided

        Raises:
            ValueError: If recipe format is invalid or step execution fails
            TypeError: If recipe type is not supported
        """
        if logger is None:
            logger = logging.getLogger(__name__)
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            if not logger.handlers:
                logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        try:
            data: Any = None
            # Determine the type of recipe input
            if isinstance(recipe, (dict, list)):
                data = recipe
            elif isinstance(recipe, str):
                # Check if the string is a file path
                if os.path.exists(recipe):
                    with open(recipe, "r") as f:
                        file_content = f.read()
                    # Try to extract JSON from markdown fenced code block
                    json_content = extract_json_from_markdown(file_content)
                    if json_content is not None:
                        data = json.loads(json_content)
                    else:
                        data = json.loads(file_content)
                else:
                    # Assume it's a JSON string
                    data = json.loads(recipe)
            else:
                raise TypeError("Unsupported recipe type provided.")

            # Extract steps from the loaded data
            steps: Any = None
            if isinstance(data, dict):
                if "steps" in data:
                    steps = data["steps"]
                else:
                    steps = data
            else:
                steps = data

            if not isinstance(steps, list):
                raise ValueError("Invalid recipe format: steps must be a list.")

            # Execute each step sequentially
            for idx, step in enumerate(steps):
                if not isinstance(step, dict):
                    raise ValueError(f"Step at index {idx} is not a valid dictionary.")
                if "type" not in step:
                    raise ValueError(f"Step at index {idx} is missing a 'type' field.")

                step_type = step["type"]
                if step_type not in STEP_REGISTRY:
                    raise ValueError(f"Unknown step type '{step_type}' at index {idx}.")

                step_class = STEP_REGISTRY[step_type]
                step_instance = step_class(step, logger)
                logger.info(f"Executing step {idx} of type '{step_type}'.")
                try:
                    step_instance.execute(context)
                except Exception as e:
                    logger.exception(f"Error executing step {idx} of type '{step_type}': {str(e)}")
                    raise ValueError(f"Step execution failed at index {idx}: {str(e)}") from e

        except Exception as e:
            logger.exception(f"Recipe execution failed: {str(e)}")
            raise
