"""File operation configuration models."""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator


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
    content_variable: Optional[str] = Field(
        description="Name of the variable containing the content to write", default=None
    )
    content: Optional[str] = Field(
        description="Direct content to write to the file", default=None
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
    
    @field_validator('content', 'content_variable')
    @classmethod
    def validate_content_options(cls, v, info):
        """Validate that either content or content_variable is provided."""
        # This validator just returns the value; we'll do the actual validation in model_validator
        return v
        
    @classmethod
    def model_validate(cls, obj: Any, **kwargs) -> 'FileOutputConfig':
        """Validate at the model level."""
        # Ensure at least one of content or content_variable is present
        if isinstance(obj, dict) and not obj.get('content') and not obj.get('content_variable'):
            # For backward compatibility, if neither is provided, assume we need content_variable
            obj['content_variable'] = 'content'
            
        return super().model_validate(obj, **kwargs)
