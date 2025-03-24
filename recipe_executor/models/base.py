"""Base models for the Recipe Executor system."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RecipeMetadata(BaseModel):
    """Metadata about a recipe."""

    name: str = Field(description="Name of the recipe")
    description: Optional[str] = Field(
        description="Description of what the recipe does", default=None
    )
    author: Optional[str] = Field(description="Author of the recipe", default=None)
    version: Optional[str] = Field(description="Version of the recipe", default=None)
    created: Optional[datetime] = Field(
        description="Creation date of the recipe", default=None
    )
    tags: Optional[List[str]] = Field(
        description="Tags associated with the recipe", default=None
    )
    timeout: Optional[int] = Field(
        description="Global timeout in seconds for the recipe execution", default=None
    )


class FileOutput(BaseModel):
    """Represents a file to be written to disk."""

    path: str = Field(description="The path to write the file to")
    content: str = Field(description="The content to write to the file")
    is_new: bool = Field(
        description="Whether this is a new file or a replacement for an existing file"
    )


class FilesGenerationResult(BaseModel):
    """Result of a file generation operation."""

    files: List[FileOutput] = Field(description="Files to write to disk")
    completed: bool = Field(
        description="Whether the generation was completed successfully"
    )
    message: Optional[str] = Field(
        description="Optional message about the generation", default=None
    )
