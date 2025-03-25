"""Event classes for execution progress tracking."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from recipe_executor.constants import ExecutionStatus, StepStatus, StepType


class ExecutionEvent(BaseModel):
    """Base class for execution events."""

    timestamp: datetime = Field(
        description="When the event occurred", default_factory=datetime.now
    )
    event_type: str = Field(description="Type of event")


class StepStartEvent(ExecutionEvent):
    """Event emitted when a step starts."""

    event_type: str = "step_start"
    step_id: str = Field(description="ID of the step")
    step_name: Optional[str] = Field(description="Name of the step", default=None)
    step_type: StepType = Field(description="Type of the step")


class StepCompleteEvent(ExecutionEvent):
    """Event emitted when a step completes."""

    event_type: str = "step_complete"
    step_id: str = Field(description="ID of the step")
    status: StepStatus = Field(description="Status of the step")
    duration_seconds: float = Field(
        description="Duration of the step execution in seconds"
    )


class StepFailedEvent(ExecutionEvent):
    """Event emitted when a step fails."""

    event_type: str = "step_failed"
    step_id: str = Field(description="ID of the step")
    error: str = Field(description="Error message")
    traceback: Optional[str] = Field(description="Error traceback", default=None)


class ValidationEvent(ExecutionEvent):
    """Event emitted during validation."""

    event_type: str = "validation"
    valid: bool = Field(description="Whether validation passed")
    issues_count: int = Field(description="Number of validation issues")


class LLMGenerationEvent(ExecutionEvent):
    """Event emitted during LLM generation."""

    event_type: str = "llm_generation"
    model: str = Field(description="Model used")
    prompt_length: int = Field(description="Length of the prompt in characters")


class UserInteractionEvent(ExecutionEvent):
    """Event emitted when user interaction is required."""

    event_type: str = "user_interaction"
    prompt: str = Field(description="Prompt shown to the user")


class RecipeStartEvent(ExecutionEvent):
    """Event emitted when a recipe starts."""

    event_type: str = "recipe_start"
    recipe_name: str = Field(description="Name of the recipe")
    description: Optional[str] = Field(description="Description of the recipe", default="")


class RecipeCompleteEvent(ExecutionEvent):
    """Event emitted when a recipe completes."""

    event_type: str = "recipe_complete"
    recipe_name: str = Field(description="Name of the recipe")
    status: ExecutionStatus = Field(description="Status of the recipe execution")
    duration_seconds: float = Field(
        description="Duration of the recipe execution in seconds"
    )
    error: Optional[str] = Field(description="Error message if execution failed", default=None)
