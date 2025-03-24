"""
Recipe Executor - A robust tool for executing LLM "recipes" with code-driven reliability.

This package enables executing natural language or structured workflow definitions
with strong validation, error handling, and context management.
"""

__version__ = "0.1.0"

# Export public API
from recipe_executor.constants import (
    ExecutionStatus,
    InteractionMode,
    OutputFormat,
    StepStatus,
    StepType,
    ValidationLevel,
)
from recipe_executor.context.execution_context import ExecutionContext
from recipe_executor.events.event_system import EventListener
from recipe_executor.events.listeners.console import ConsoleEventListener
from recipe_executor.main import RecipeExecutor
from recipe_executor.models.execution import RecipeResult, StepResult
from recipe_executor.models.recipe import Recipe
from recipe_executor.models.step import RecipeStep
from recipe_executor.models.validation import ValidationIssue, ValidationResult

__all__ = [
    "RecipeExecutor",
    "Recipe",
    "RecipeStep",
    "StepType",
    "OutputFormat",
    "ValidationLevel",
    "InteractionMode",
    "ExecutionStatus",
    "StepStatus",
    "RecipeResult",
    "StepResult",
    "ValidationResult",
    "ValidationIssue",
    "ExecutionContext",
    "EventListener",
    "ConsoleEventListener",
]
