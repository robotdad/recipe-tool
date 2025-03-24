"""User input executor implementation."""

import asyncio
import logging
from typing import Any

from recipe_executor.context.execution_context import ExecutionContext
from recipe_executor.models.events import UserInteractionEvent
from recipe_executor.models.step import RecipeStep
from recipe_executor.models.validation import ValidationIssue, ValidationResult

logger = logging.getLogger("recipe-executor")


class WaitForInputExecutor:
    """Executor for wait for input steps."""

    async def execute(self, step: RecipeStep, context: ExecutionContext) -> Any:
        """
        Execute a wait for input step.

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            User input
        """
        if not step.wait_for_input:
            raise ValueError(f"Missing wait_for_input configuration for step {step.id}")

        config = step.wait_for_input

        # Interpolate the prompt
        prompt = context.interpolate_variables(config.prompt)

        # Emit user interaction event
        event = UserInteractionEvent(prompt=prompt)
        context.emit_event(event)

        # Set up timeout
        timeout = config.timeout
        if timeout is None and step.timeout:
            timeout = step.timeout
        if timeout is None and context.recipe and context.recipe.timeout:
            timeout = context.recipe.timeout

        # Wait for input with timeout if specified
        if timeout:
            try:
                input_task = asyncio.create_task(asyncio.to_thread(input, prompt + " "))
                result = await asyncio.wait_for(input_task, timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning(
                    f"Wait for input timed out after {timeout}s for step {step.id}"
                )
                result = config.default_value
        else:
            result = input(prompt + " ")

        # Process options if specified
        if config.options and result:
            if result.isdigit() and 0 <= int(result) < len(config.options):
                # User entered a numeric index
                result = config.options[int(result)]
            elif result not in config.options:
                # User entered something not in the options
                print(f"Invalid option: {result}")
                print(f"Valid options: {', '.join(config.options)}")
                if config.default_value is not None:
                    result = config.default_value
                else:
                    # Try again
                    return await self.execute(step, context)

        # Use default value if input is empty
        if not result and config.default_value is not None:
            result = config.default_value

        return result

    async def validate_result(
        self, step: RecipeStep, result: Any, context: ExecutionContext
    ) -> ValidationResult:
        """
        Validate the result of a wait for input step.

        Args:
            step: Step to validate
            result: Result to validate
            context: Execution context

        Returns:
            Validation result
        """
        if not step.wait_for_input:
            return ValidationResult(valid=True, issues=[])

        config = step.wait_for_input

        # Check that the result is not None if required
        if result is None and not config.default_value:
            return ValidationResult(
                valid=False,
                issues=[
                    ValidationIssue(
                        message="Input is required but was not provided",
                        severity="error",
                    )
                ],
            )

        # Check that the result is in the options if specified
        if config.options and result not in config.options:
            return ValidationResult(
                valid=False,
                issues=[
                    ValidationIssue(
                        message=f"Input '{result}' is not in the valid options: {', '.join(config.options)}",
                        severity="error",
                    )
                ],
            )

        return ValidationResult(valid=True, issues=[])
