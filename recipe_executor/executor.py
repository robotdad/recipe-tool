import json
import logging
import os
import re
from typing import Optional

from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY


class RecipeExecutor:
    """
    Unified executor that loads a recipe (from a file path, JSON string, or dict),
    and executes its steps sequentially using the provided context.
    """

    def execute(self, recipe, context: Context, logger: Optional[logging.Logger] = None) -> None:
        logger = logger or logging.getLogger("RecipeExecutor")

        # Load recipe data from different input types.
        if isinstance(recipe, str):
            if os.path.isfile(recipe):
                logger.debug("Loading recipe file: %s", recipe)
                with open(recipe, "r", encoding="utf-8") as f:
                    content = f.read()

                # Try to extract JSON from a fenced code block (```json ... ```)
                match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
                if match:
                    snippet = match.group(1).strip()
                    if not snippet:
                        raise ValueError("The JSON code block in the recipe file is empty.")
                    logger.debug("Extracted JSON snippet: %s", snippet)
                    try:
                        recipe_data = json.loads(snippet)
                    except Exception as e:
                        logger.error(
                            "Failed to parse JSON from the code block. Raw snippet: %s", snippet, exc_info=True
                        )
                        raise e
                else:
                    # Fallback: try to parse the entire file as JSON
                    content_stripped = content.strip()
                    if not content_stripped:
                        raise ValueError("Recipe file is empty.")
                    logger.debug(
                        "No fenced JSON found. Using entire file content for JSON parsing. Content: %s",
                        content_stripped,
                    )
                    try:
                        recipe_data = json.loads(content_stripped)
                    except Exception as e:
                        logger.error(
                            "Failed to parse the entire recipe file as JSON. File content: %s", content, exc_info=True
                        )
                        raise e
            else:
                # If the string is not a file path, treat it as a JSON string.
                try:
                    recipe_data = json.loads(recipe)
                except Exception as e:
                    logger.error("Failed to parse the recipe string as JSON. Recipe string: %s", recipe, exc_info=True)
                    raise e
        elif isinstance(recipe, dict):
            recipe_data = recipe
        else:
            raise TypeError("Recipe must be a file path, JSON string, or a dictionary.")

        # Extract steps: if recipe_data is a dict with a 'steps' key, use it; otherwise, assume it's a list.
        if isinstance(recipe_data, dict) and "steps" in recipe_data:
            steps = recipe_data["steps"]
        elif isinstance(recipe_data, list):
            steps = recipe_data
        else:
            raise ValueError("Recipe data must be a list of steps or a dict with a 'steps' key.")

        logger.info(f"Loaded recipe with {len(steps)} steps.")

        # Execute each step sequentially.
        for idx, step_def in enumerate(steps):
            if not isinstance(step_def, dict):
                raise ValueError(f"Step {idx + 1} is not a valid dictionary.")

            step_type = step_def.get("type")
            if not step_type:
                raise ValueError(f"Step {idx + 1} is missing the 'type' field.")

            step_cls = STEP_REGISTRY.get(step_type)
            if step_cls is None:
                raise ValueError(f"Unknown step type '{step_type}' in step {idx + 1}.")

            logger.info(f"Executing step {idx + 1}: {step_type}")
            try:
                # Instantiate and execute the step.
                step_instance = step_cls(config=step_def, logger=logger)
                step_instance.execute(context)
                logger.info(f"Completed step {idx + 1}: {step_type}")
            except Exception as e:
                logger.error(f"Error executing step {idx + 1} ({step_type}): {e}", exc_info=True)
                raise e
