"""Python execution configuration model."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PythonExecuteConfig(BaseModel):
    """Configuration for executing Python code."""

    code: str = Field(description="Python code to execute")
    code_file: Optional[str] = Field(
        description="Path to file containing Python code", default=None
    )
    input_variables: Dict[str, str] = Field(
        description="Variables to pass to the code", default_factory=dict
    )
    output_variable: str = Field(
        description="Name of the variable to store the result in"
    )
    timeout: Optional[int] = Field(
        description="Timeout in seconds for code execution", default=30
    )
    validation_code: Optional[str] = Field(
        description="Python code to validate the output", default=None
    )
    memory_limit_mb: Optional[int] = Field(
        description="Memory limit in MB for code execution", default=None
    )
    allowed_imports: Optional[List[str]] = Field(
        description="List of modules allowed to be imported", default=None
    )
