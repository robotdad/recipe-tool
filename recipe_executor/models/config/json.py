"""JSON processing configuration."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class JsonProcessConfig(BaseModel):
    """Configuration for JSON processing."""

    input_variable: str = Field(
        description="Name of the variable containing the JSON to process"
    )
    operations: List[Dict[str, Any]] = Field(
        description="Operations to perform on the JSON"
    )
    output_variable: str = Field(
        description="Name of the variable to store the result in"
    )
    validation_schema: Optional[Dict[str, Any]] = Field(
        description="JSON schema for validating the result", default=None
    )
