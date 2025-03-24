"""Recipe model definition."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from recipe_executor.constants import InteractionMode, ValidationLevel
from recipe_executor.models.base import RecipeMetadata
from recipe_executor.models.config.model import ModelConfig
from recipe_executor.models.step import RecipeStep


class Recipe(BaseModel):
    """A complete recipe for the LLM to execute."""

    metadata: RecipeMetadata = Field(description="Metadata about the recipe")
    defaults: Optional[Dict[str, Any]] = Field(
        description="Default values to use throughout the recipe", default=None
    )
    model: Optional["ModelConfig"] = Field(
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
