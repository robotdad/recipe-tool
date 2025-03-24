"""File operation configuration models."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class FileInputConfig(BaseModel):
    """Configuration for file input."""

    path: str = Field(description="Path to the file to read")
    pattern: Optional[str] = Field(
        description="Glob pattern for multiple files", default=None
    )
    encoding: str = Field(
        description="Encoding to use when reading the file", default="utf-8"
    )
    as_variable: str = Field(
        description="Name of the variable to store the file content in"
    )


class FileOutputConfig(BaseModel):
    """Configuration for file output."""

    path: str = Field(description="Path to write the file to")
    content_variable: str = Field(
        description="Name of the variable containing the content to write"
    )
    encoding: str = Field(
        description="Encoding to use when writing the file", default="utf-8"
    )
    mode: Literal["w", "a"] = Field(
        description="Write mode - 'w' for write, 'a' for append", default="w"
    )
    mkdir: bool = Field(
        description="Whether to create directories if they don't exist", default=True
    )
