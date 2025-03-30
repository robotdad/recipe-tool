import logging
import os
from typing import Any, Dict, Optional

from recipe_executor.context import Context
from recipe_executor.executor import RecipeExecutor
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class ExecuteRecipeConfig(StepConfig):
    """Config for ExecuteRecipeStep.

    Fields:
        recipe_path: Path to the recipe to execute.
        context_overrides: Optional values to override in the context.
    """

    recipe_path: str
    context_overrides: Dict[str, str] = {}


class ExecuteRecipeStep(BaseStep[ExecuteRecipeConfig]):
    """Step for executing a sub-recipe with dynamic path rendering and context overrides.

    This step applies template rendering to both the recipe path and context overrides,
    verifies the existence of the sub-recipe file, and then uses the RecipeExecutor to execute it.
    Detailed logging is performed to track execution start and completion.
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None) -> None:
        # Convert dict config to an instance of ExecuteRecipeConfig
        super().__init__(ExecuteRecipeConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute a sub-recipe by applying context overrides, rendering the recipe path,
        and delegating execution to RecipeExecutor.

        Args:
            context (Context): Shared context between parent and sub-recipe.

        Raises:
            FileNotFoundError: If the sub-recipe file does not exist.
            Exception: Propagates exceptions from sub-recipe execution.
        """
        # Apply context overrides if specified
        if self.config.context_overrides:
            for key, value in self.config.context_overrides.items():
                rendered_value = render_template(value, context)
                context[key] = rendered_value

        # Render the sub-recipe path
        recipe_path = render_template(self.config.recipe_path, context)

        # Verify that the sub-recipe file exists
        if not os.path.exists(recipe_path):
            error_message = f"Sub-recipe file not found: {recipe_path}"
            self.logger.error(error_message)
            raise FileNotFoundError(error_message)

        # Log the start of sub-recipe execution
        self.logger.info(f"Executing sub-recipe: {recipe_path}")

        # Execute the sub-recipe using the RecipeExecutor
        try:
            executor = RecipeExecutor()
            executor.execute(recipe=recipe_path, context=context, logger=self.logger)
        except Exception as e:
            self.logger.error(f"Error executing sub-recipe '{recipe_path}': {e}")
            raise

        # Log the completion of sub-recipe execution
        self.logger.info(f"Completed sub-recipe: {recipe_path}")
