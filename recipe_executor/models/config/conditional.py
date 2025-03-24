"""Conditional execution configuration model."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ConditionalConfig(BaseModel):
    """Configuration for conditional execution."""

    condition: str = Field(description="Condition to evaluate")
    true_step: Dict[str, Any] = Field(
        description="Step to execute if condition is true"
    )
    false_step: Optional[Dict[str, Any]] = Field(
        description="Step to execute if condition is false", default=None
    )
