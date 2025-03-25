"""Registry of executor functions for recipe steps."""

import asyncio
from typing import Any, Callable, Dict, Optional, Protocol, runtime_checkable

from recipe_executor.constants import StepType
from recipe_executor.context.simple_context import ExecutionContext
from recipe_executor.models.step import RecipeStep
from recipe_executor.models.validation import ValidationResult
from recipe_executor.utils import logging as log_utils

logger = log_utils.get_logger("executors")

# Type for executor functions
ExecutorFunc = Callable[[RecipeStep, ExecutionContext], Any]

# Registry of executor functions
_executor_registry: Dict[StepType, ExecutorFunc] = {}


def register_executor(step_type: StepType):
    """Decorator to register an executor function for a step type."""

    def decorator(func: ExecutorFunc) -> ExecutorFunc:
        _executor_registry[step_type] = func
        return func

    return decorator


def get_executor(step_type: StepType) -> ExecutorFunc:
    """Get the executor function for a step type."""
    if step_type not in _executor_registry:
        raise ValueError(f"No executor registered for step type: {step_type}")
    return _executor_registry[step_type]


async def validate_result(
    step: RecipeStep, result: Any, context: ExecutionContext
) -> ValidationResult:
    """Common validation function for all executors."""
    # Get validation criteria from step config if available
    validation_config = None
    if hasattr(step, f"{step.type.value}") and hasattr(
        getattr(step, f"{step.type.value}"), "validation_criteria"
    ):
        validation_config = getattr(getattr(step, f"{step.type.value}"), "validation_criteria")

    if not validation_config:
        # No specific validation criteria defined
        return ValidationResult(valid=True, issues=[])

    # Implement common validation logic based on validation_config
    # This replaces the per-executor validation logic
    # ...

    # For now, return a default result
    return ValidationResult(valid=True, issues=[])
