"""Validation models for the Recipe Executor system."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ValidationIssue(BaseModel):
    """Represents an issue found during validation."""

    message: str = Field(description="Description of the issue")
    severity: Literal["error", "warning", "info"] = Field(
        description="Severity of the issue"
    )
    path: Optional[str] = Field(
        description="Path to the element with the issue", default=None
    )
    context: Optional[Dict[str, Any]] = Field(
        description="Additional context about the issue", default=None
    )


class ValidationResult(BaseModel):
    """Result of a validation operation."""

    valid: bool = Field(description="Whether the validation passed")
    issues: List[ValidationIssue] = Field(
        description="Issues found during validation", default_factory=list
    )
    metadata: Dict[str, Any] = Field(
        description="Additional metadata about the validation", default_factory=dict
    )
