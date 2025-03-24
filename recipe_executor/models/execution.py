"""Execution state and result models."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from recipe_executor.constants import ExecutionStatus, StepStatus
from recipe_executor.models.validation import ValidationResult


class StepResult(BaseModel):
    """Result of a step execution."""

    step_id: str = Field(description="ID of the step")
    status: StepStatus = Field(description="Status of the step execution")
    result: Any = Field(description="Result of the step execution", default=None)
    error: Optional[str] = Field(
        description="Error message if the step failed", default=None
    )
    started_at: datetime = Field(description="When the step started")
    completed_at: Optional[datetime] = Field(
        description="When the step completed", default=None
    )
    duration_seconds: Optional[float] = Field(
        description="Duration of the step execution in seconds", default=None
    )
    validation_result: Optional[ValidationResult] = Field(
        description="Result of validation", default=None
    )
    metadata: Dict[str, Any] = Field(
        description="Additional metadata about the step execution", default_factory=dict
    )


class RecipeResult(BaseModel):
    """Result of a recipe execution."""

    recipe_name: str = Field(description="Name of the recipe")
    status: ExecutionStatus = Field(description="Status of the recipe execution")
    started_at: datetime = Field(description="When the recipe started")
    completed_at: Optional[datetime] = Field(
        description="When the recipe completed", default=None
    )
    duration_seconds: Optional[float] = Field(
        description="Duration of the recipe execution in seconds", default=None
    )
    steps: Dict[str, StepResult] = Field(
        description="Results of step executions", default_factory=dict
    )
    variables: Dict[str, Any] = Field(
        description="Final variables after recipe execution", default_factory=dict
    )
    error: Optional[str] = Field(
        description="Error message if the recipe failed", default=None
    )
