"""Chain execution configuration model."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChainConfig(BaseModel):
    """Configuration for chaining steps."""

    steps: List[Dict[str, Any]] = Field(
        description="List of steps to execute in sequence"
    )
    output_variable: Optional[str] = Field(
        description="Name of the variable to store the final result in", default=None
    )
    shared_variables: Optional[List[str]] = Field(
        description="List of variables to share within the chain", default=None
    )
    continue_on_step_failure: bool = Field(
        description="Whether to continue if a step fails", default=False
    )
