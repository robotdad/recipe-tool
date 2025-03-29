from typing import Any

from context import Context
from models import Recipe
from steps import get_step_instance


class Executor:
    def __init__(self, recipe: Recipe, context: Context, logger: Any) -> None:
        """
        Initialize the Executor.

        Args:
            recipe (Recipe): The recipe object containing the list of steps.
            context (Context): A dictionary holding shared context, including keys like 'input_root' and 'output_root'.
            logger (Any): The logger instance to use for logging messages.
        """
        self.recipe = recipe
        self.context = context
        self.logger = logger

    def execute(self) -> None:
        """
        Execute each step in the recipe sequentially.

        Logs the start and completion of each step. If a step raises an exception, it is logged and then re-raised.
        """
        self.logger.info(f"Executor: Starting execution of recipe with {len(self.recipe.steps)} steps.")
        for idx, step in enumerate(self.recipe.steps, start=1):
            self.logger.info(f"Executor: Executing step {idx}: {step.type}.")
            try:
                step_instance = get_step_instance(step.type, step.config, self.logger)
                step_instance.execute(self.context)
                self.logger.info(f"Executor: Completed step {idx}: {step.type}.")
            except Exception as e:
                self.logger.error(f"Executor: Error in step {idx} ({step.type}): {e}", exc_info=True)
                raise
        self.logger.info("Executor: Recipe execution completed.")
