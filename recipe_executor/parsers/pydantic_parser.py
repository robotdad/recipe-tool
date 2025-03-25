"""Natural language recipe parser using pydantic-ai."""

from typing import Any, Dict, Optional, Type, TypeVar, cast

from pydantic import BaseModel

from recipe_executor.constants import DEFAULT_MODEL_NAME, DEFAULT_MODEL_PROVIDER, DEFAULT_TEMPERATURE
from recipe_executor.models.recipe import Recipe
from recipe_executor.parsers.formats import parse_natural_language
from recipe_executor.utils import logging as log_utils

# Type var for generic parsing results
T = TypeVar("T", bound=BaseModel)

# Setup logging
logger = log_utils.get_logger("parser")


class RecipeParser:
    """
    Parser for natural language recipes using pydantic-ai.
    This class wraps the parse_natural_language function to provide a consistent interface.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        model_provider: str = DEFAULT_MODEL_PROVIDER,
        temperature: float = DEFAULT_TEMPERATURE,
    ):
        """
        Initialize the recipe parser.

        Args:
            model_name: The model to use for parsing
            model_provider: The provider of the model
            temperature: Temperature for generation
        """
        self.model_name = model_name
        self.model_provider = model_provider
        self.temperature = temperature

    async def parse_recipe_from_text(self, content: str) -> Recipe:
        """
        Parse natural language text into a structured Recipe.

        Args:
            content: The natural language recipe content

        Returns:
            A Recipe pydantic model
        """
        logger.info(f"Parsing as natural language recipe using pydantic-ai")
        
        # Use the parse_natural_language function from formats module
        return await parse_natural_language(
            content,
            Recipe,
            self.model_name,
            self.model_provider,
            self.temperature
        )

    async def parse_to_model(self, content: str, model_class: Type[T], context: Optional[str] = None) -> T:
        """
        Parse natural language content into any specified pydantic model.

        Args:
            content: The natural language content
            model_class: The pydantic model class to parse into
            context: Optional context to help the LLM understand the structure

        Returns:
            An instance of the specified model class
        """
        # We can use the same parse_natural_language function but with a different model class
        return await parse_natural_language(
            content,
            model_class,
            self.model_name,
            self.model_provider,
            self.temperature
        )