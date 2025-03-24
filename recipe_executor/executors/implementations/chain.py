"""Chain execution executor implementation."""

import logging
from typing import Any

from recipe_executor.constants import VariableScope
from recipe_executor.context.execution_context import ExecutionContext
from recipe_executor.models.step import RecipeStep
from recipe_executor.models.validation import ValidationResult

logger = logging.getLogger("recipe-executor")


class ChainExecutor:
    """Executor for chain steps."""

    async def execute(self, step: RecipeStep, context: ExecutionContext) -> Any:
        """
        Execute a chain of steps.

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            Result of the last step in the chain
        """
        if not step.chain:
            raise ValueError(f"Missing chain configuration for step {step.id}")

        config = step.chain

        # Create a new context for the chain
        chain_context = context.create_child_context(VariableScope.CHAIN)

        # Copy shared variables if specified
        if config.shared_variables:
            for var_name in config.shared_variables:
                value = context.get_variable(var_name)
                if value is not None:
                    chain_context.set_variable(var_name, value)

        result = None

        # Execute each step in sequence
        for i, sub_step_data in enumerate(config.steps):
            # Create a RecipeStep from the sub-step data
            sub_step_id = sub_step_data.get("id", f"{step.id}_sub_{i + 1}")
            sub_step_data["id"] = sub_step_id
            sub_step = RecipeStep.model_validate(sub_step_data)

            # Create a clean executor for the sub-step
            from recipe_executor.main import RecipeExecutor

            executor = RecipeExecutor()

            try:
                # Execute the sub-step
                result = await executor.execute_step(sub_step, chain_context)

                # Copy the result to the chain context
                if "output_variable" in sub_step_data and isinstance(
                    sub_step_data["output_variable"], str
                ):
                    chain_context.set_variable(sub_step_data["output_variable"], result)
                elif hasattr(sub_step, f"{sub_step.type.value}") and hasattr(
                    getattr(sub_step, f"{sub_step.type.value}"), "output_variable"
                ):
                    output_variable = getattr(
                        getattr(sub_step, f"{sub_step.type.value}"), "output_variable"
                    )
                    if output_variable:
                        chain_context.set_variable(output_variable, result)
            except Exception as e:
                logger.error(f"Error executing sub-step {sub_step_id}: {e}")
                if not config.continue_on_step_failure:
                    raise
                result = None

        # Copy shared variables back to the parent context
        if config.shared_variables:
            for var_name in config.shared_variables:
                value = chain_context.get_variable(var_name)
                if value is not None:
                    context.set_variable(var_name, value)

        # Store the final result if an output variable is specified
        if config.output_variable:
            context.set_variable(config.output_variable, result)

        return result

    async def validate_result(
        self, step: RecipeStep, result: Any, context: ExecutionContext
    ) -> ValidationResult:
        """
        Validate the result of a chain step.

        Args:
            step: Step to validate
            result: Result to validate
            context: Execution context

        Returns:
            Validation result
        """
        # The validation is handled by each sub-step
        return ValidationResult(valid=True, issues=[])
