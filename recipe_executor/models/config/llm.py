"""LLM generation configuration model."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from recipe_executor.constants import OutputFormat


class LLMGenerateConfig(BaseModel):
    """Configuration for LLM generation."""

    prompt: str = Field(description="Prompt to send to the LLM")
    model: Optional[str] = Field(
        description="Model ID to use for this generation", default=None
    )
    output_format: OutputFormat = Field(
        description="Format of the output", default=OutputFormat.TEXT
    )
    output_variable: str = Field(
        description="Name of the variable to store the output in"
    )
    temperature: Optional[float] = Field(
        description="Temperature for generation", default=None
    )
    include_history: bool = Field(
        description="Whether to include message history from previous steps",
        default=False,
    )
    history_variable: Optional[str] = Field(
        description="Variable containing history messages to include", default=None
    )
    retry_prompt: Optional[str] = Field(
        description="Prompt to use for retry attempts", default=None
    )
    structured_schema: Optional[Dict[str, Any]] = Field(
        description="Schema for structured output", default=None
    )
    structured_schema_file: Optional[str] = Field(
        description="Path to file containing schema for structured output", default=None
    )
    validation_criteria: Optional[Dict[str, Any]] = Field(
        description="Criteria for validating the output", default=None
    )
    timeout: Optional[int] = Field(
        description="Timeout in seconds for this generation", default=None
    )
