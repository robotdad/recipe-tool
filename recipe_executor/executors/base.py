"""Base protocol for step executors."""

from typing import Any, Protocol, runtime_checkable

from recipe_executor.context.execution_context import ExecutionContext
from recipe_executor.models.step import RecipeStep
from recipe_executor.models.validation import ValidationResult


@runtime_checkable
class StepExecutor(Protocol):
    """Interface for step executors."""

    async def execute(self, step: RecipeStep, context: ExecutionContext) -> Any:
        """Execute a step with the given context."""
        ...

    async def validate_result(
        self, step: RecipeStep, result: Any, context: ExecutionContext
    ) -> ValidationResult:
        """Validate the result of a step execution."""
        ...
