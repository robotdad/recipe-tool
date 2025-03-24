"""Validator configuration model."""

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


class ValidatorConfig(BaseModel):
    """Configuration for validation steps."""

    target_variable: str = Field(description="Name of the variable to validate")
    validation_type: Literal["schema", "code", "llm"] = Field(
        description="Type of validation to perform"
    )
    validation_schema: Optional[Dict[str, Any]] = Field(
        description="JSON schema for validation", default=None
    )
    code: Optional[str] = Field(description="Python code for validation", default=None)
    llm_prompt: Optional[str] = Field(
        description="Prompt for LLM validation", default=None
    )
    output_variable: str = Field(
        description="Name of the variable to store validation result in"
    )
    error_message: Optional[str] = Field(
        description="Custom error message for validation failures", default=None
    )
