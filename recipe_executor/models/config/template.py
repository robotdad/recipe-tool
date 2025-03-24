"""Template substitution configuration."""

from typing import Dict, Optional

from pydantic import BaseModel, Field


class TemplateSubstituteConfig(BaseModel):
    """Configuration for template substitution."""

    template: str = Field(description="Template to substitute variables into")
    template_file: Optional[str] = Field(
        description="Path to file containing the template", default=None
    )
    variables: Dict[str, str] = Field(
        description="Variables to substitute into the template", default_factory=dict
    )
    output_variable: str = Field(
        description="Name of the variable to store the result in"
    )
