"""Recipe model definition."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from recipe_executor.constants import InteractionMode, ValidationLevel
from recipe_executor.models.step import RecipeStep


class RecipeMetadata(BaseModel):
    """Metadata about a recipe."""
    
    name: str = Field(description="Name of the recipe")
    description: Optional[str] = Field(description="Description of what the recipe does", default=None)
    author: Optional[str] = Field(description="Author of the recipe", default=None)
    version: Optional[str] = Field(description="Version of the recipe", default=None)
    tags: Optional[List[str]] = Field(description="Tags for the recipe", default=None)


class ModelConfig(BaseModel):
    """Configuration for the LLM model to use."""
    
    # The name field is the primary field
    name: str = Field(description="Name of the model to use")
    
    # model_name is an alias for name to maintain compatibility with old code
    # We use a computed field that returns name value to avoid duplication
    @property
    def model_name(self) -> str:
        """Return the name of the model (alias for name field)."""
        return self.name
        
    provider: Optional[str] = Field(
        description="Provider of the model", default=None
    )
    temperature: Optional[float] = Field(
        description="Temperature setting for model generation", default=None
    )
    max_tokens: Optional[int] = Field(
        description="Maximum tokens to generate", default=None
    )
    system_prompt: Optional[str] = Field(
        description="System prompt to use for all LLM interactions", default=None
    )


class Recipe(BaseModel):
    """A complete recipe for the LLM to execute."""

    metadata: RecipeMetadata = Field(description="Metadata about the recipe")
    model: Optional[ModelConfig] = Field(
        description="Global model configuration for the recipe", default=None
    )
    variables: Dict[str, Any] = Field(
        description="Initial variables for the recipe", default_factory=dict
    )
    steps: List[RecipeStep] = Field(description="Steps to execute in the recipe")
    validation_level: ValidationLevel = Field(
        description="Default validation level for all steps",
        default=ValidationLevel.STANDARD,
    )
    interaction_mode: InteractionMode = Field(
        description="How the executor interacts with users",
        default=InteractionMode.CRITICAL,
    )
    max_retries: int = Field(description="Default maximum retries for steps", default=3)
    timeout: Optional[int] = Field(
        description="Overall timeout for the entire recipe in seconds", default=None
    )