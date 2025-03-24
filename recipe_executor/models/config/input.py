"""User input configuration model."""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class WaitForInputConfig(BaseModel):
    """Configuration for waiting for user input."""

    prompt: str = Field(description="Prompt to show to the user")
    output_variable: str = Field(
        description="Name of the variable to store user input in"
    )
    default_value: Optional[Any] = Field(
        description="Default value if no input is provided", default=None
    )
    timeout: Optional[int] = Field(
        description="Timeout in seconds for waiting for input", default=None
    )
    options: Optional[List[str]] = Field(
        description="List of options for the user to choose from", default=None
    )
