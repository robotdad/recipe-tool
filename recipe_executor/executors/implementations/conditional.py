"""Conditional execution executor implementation."""

import logging
from typing import Any

from recipe_executor.context.execution_context import ExecutionContext
from recipe_executor.models.step import RecipeStep
from recipe_executor.models.validation import ValidationResult

logger = logging.getLogger("recipe-executor")


class ConditionalExecutor:
    """Executor for conditional steps."""

    async def execute(self, step: RecipeStep, context: ExecutionContext) -> Any:
        """
        Execute a conditional step.

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            Result of the executed branch
        """
        if not step.conditional:
            raise ValueError(f"Missing conditional configuration for step {step.id}")

        config = step.conditional

        # Evaluate the condition
        condition = context.interpolate_variables(config.condition)
        condition_result = context.evaluate_condition(condition)

        logger.info(f"Condition '{condition}' evaluated to {condition_result}")

        if condition_result:
            # Execute the true branch
            true_step = config.true_step
            true_step_obj = RecipeStep.model_validate(true_step)

            # Create a clean executor for the sub-step
            from recipe_executor.main import RecipeExecutor

            executor = RecipeExecutor()

            return await executor.execute_step(true_step_obj, context)
        elif config.false_step:
            # Execute the false branch
            false_step = config.false_step
            false_step_obj = RecipeStep.model_validate(false_step)

            # Create a clean executor for the sub-step
            from recipe_executor.main import RecipeExecutor

            executor = RecipeExecutor()

            return await executor.execute_step(false_step_obj, context)
        else:
            # No false branch, return None
            return None

    async def validate_result(
        self, step: RecipeStep, result: Any, context: ExecutionContext
    ) -> ValidationResult:
        """
        Validate the result of a conditional step.

        Args:
            step: Step to validate
            result: Result to validate
            context: Execution context

        Returns:
            Validation result
        """
        # The validation is handled by the executed branch
        return ValidationResult(valid=True, issues=[])
