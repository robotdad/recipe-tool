"""Parallel execution executor implementation."""

import asyncio
import logging
from typing import Any, List

from recipe_executor.constants import VariableScope
from recipe_executor.context.execution_context import ExecutionContext
from recipe_executor.models.step import RecipeStep
from recipe_executor.models.validation import ValidationResult

logger = logging.getLogger("recipe-executor")


class ParallelExecutor:
    """Executor for parallel steps."""

    async def execute(self, step: RecipeStep, context: ExecutionContext) -> List[Any]:
        """
        Execute steps in parallel.

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            List of results from each step
        """
        if not step.parallel:
            raise ValueError(f"Missing parallel configuration for step {step.id}")

        config = step.parallel

        # Create a new context for each parallel step
        step_contexts = [
            context.create_child_context(VariableScope.STEP) for _ in config.steps
        ]

        # Create tasks for each sub-step
        tasks = []
        for i, (sub_step_data, step_context) in enumerate(
            zip(config.steps, step_contexts)
        ):
            # Create a RecipeStep from the sub-step data
            sub_step_id = sub_step_data.get("id", f"{step.id}_sub_{i + 1}")
            sub_step_data["id"] = sub_step_id
            sub_step = RecipeStep.model_validate(sub_step_data)

            # Create a clean executor for the sub-step
            from recipe_executor.main import RecipeExecutor

            executor = RecipeExecutor()

            # Create a task for the sub-step
            task = asyncio.create_task(executor.execute_step(sub_step, step_context))
            tasks.append((task, sub_step_id, sub_step, step_context, sub_step_data))

        # Set up timeout
        timeout = config.timeout
        if timeout is None and step.timeout:
            timeout = step.timeout
        if timeout is None and context.recipe and context.recipe.timeout:
            timeout = context.recipe.timeout

        # Execute all tasks with timeout if specified
        if timeout:
            try:
                done, pending = await asyncio.wait(
                    [task for task, _, _, _ in tasks],
                    timeout=timeout,
                    return_when=asyncio.ALL_COMPLETED,
                )

                # Cancel any pending tasks
                for task in pending:
                    task.cancel()

                # Collect results
                results = []
                for task, sub_step_id, sub_step, step_context, sub_step_data in tasks:
                    if task in done:
                        try:
                            # Get both the result and step_result from the task
                            result, _ = task.result()
                            results.append(result)

                            # Copy result to parent context if output variable specified
                            if isinstance(sub_step_data.get("output_variable"), str):
                                context.set_variable(
                                    sub_step_data["output_variable"], result
                                )
                            elif hasattr(
                                sub_step, f"{sub_step.type.value}"
                            ) and hasattr(
                                getattr(sub_step, f"{sub_step.type.value}"),
                                "output_variable",
                            ):
                                output_variable = getattr(
                                    getattr(sub_step, f"{sub_step.type.value}"),
                                    "output_variable",
                                )
                                if output_variable:
                                    context.set_variable(output_variable, result)
                        except Exception as e:
                            logger.error(f"Error in parallel step {sub_step_id}: {e}")
                            if not step.continue_on_error:
                                raise
                            results.append(None)
                    else:
                        logger.warning(f"Parallel step {sub_step_id} timed out")
                        results.append(None)

                # Store combined results if specified
                if config.output_variable:
                    context.set_variable(config.output_variable, results)

                return results
            except asyncio.TimeoutError:
                logger.error(
                    f"Parallel execution timed out after {timeout}s for step {step.id}"
                )
                raise TimeoutError(f"Parallel execution timed out after {timeout}s")
        else:
            # Execute without timeout
            results = []
            for task, sub_step_id, sub_step, step_context, sub_step_data in tasks:
                try:
                    # Get both the result and step_result from the task
                    result, _ = await task
                    results.append(result)

                    # Copy result to parent context if output variable specified
                    if isinstance(sub_step_data.get("output_variable"), str):
                        context.set_variable(sub_step_data["output_variable"], result)
                    elif hasattr(sub_step, f"{sub_step.type.value}") and hasattr(
                        getattr(sub_step, f"{sub_step.type.value}"), "output_variable"
                    ):
                        output_variable = getattr(
                            getattr(sub_step, f"{sub_step.type.value}"),
                            "output_variable",
                        )
                        if output_variable:
                            context.set_variable(output_variable, result)
                except Exception as e:
                    logger.error(f"Error in parallel step {sub_step_id}: {e}")
                    if not step.continue_on_error:
                        raise
                    results.append(None)

            # Store combined results if specified
            if config.output_variable:
                context.set_variable(config.output_variable, results)

            return results

    async def validate_result(
        self, step: RecipeStep, result: Any, context: ExecutionContext
    ) -> ValidationResult:
        """
        Validate the result of a parallel step.

        Args:
            step: Step to validate
            result: Result to validate
            context: Execution context

        Returns:
            Validation result
        """
        # The validation is handled by each sub-step
        return ValidationResult(valid=True, issues=[])
