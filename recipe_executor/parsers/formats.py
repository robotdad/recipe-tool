"""Format-specific adapters for loading recipes."""

import json
import re
from typing import Any, Dict, Optional, Type, TypeVar

import yaml
from pydantic import BaseModel
from pydantic_ai import Agent

from recipe_executor.utils import logging as log_utils

logger = log_utils.get_logger("formats")

# Generic type for model parsing
T = TypeVar("T", bound=BaseModel)


def load_from_yaml(content: str, model_class: Type[T]) -> T:
    """Load a recipe from YAML content."""
    try:
        data = yaml.safe_load(content)
        return model_class.model_validate(data)
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error: {e}")
        raise ValueError(f"Failed to parse YAML: {e}")
    except Exception as e:
        logger.error(f"Error loading from YAML: {e}")
        raise ValueError(f"Failed to validate YAML as {model_class.__name__}: {e}")


def load_from_json(content: str, model_class: Type[T]) -> T:
    """Load a recipe from JSON content."""
    try:
        data = json.loads(content)
        return model_class.model_validate(data)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        raise ValueError(f"Failed to parse JSON: {e}")
    except Exception as e:
        logger.error(f"Error loading from JSON: {e}")
        raise ValueError(f"Failed to validate JSON as {model_class.__name__}: {e}")


def extract_structured_content(markdown: str) -> Optional[Dict[str, Any]]:
    """Extract structured content from markdown code blocks."""
    # Try YAML blocks
    yaml_match = re.search(r"```ya?ml\s*\n(.*?)\n```", markdown, re.DOTALL)
    if yaml_match:
        try:
            return yaml.safe_load(yaml_match.group(1))
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML block: {e}")

    # Try JSON blocks
    json_match = re.search(r"```json\s*\n(.*?)\n```", markdown, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON block: {e}")

    return None


async def parse_natural_language(content: str, model_class: Type[T], model_name: str, model_provider: str, temperature: float = 0.1) -> T:
    """Parse natural language content into a structured model."""
    # Create a system prompt tailored to the model class
    system_prompt = _get_parsing_system_prompt(model_class)

    # Format model ID properly for pydantic-ai
    if model_provider == "anthropic":
        model_id = (
            f"anthropic:{model_name}"
            if not model_name.startswith("anthropic:")
            else model_name
        )
    elif model_provider == "openai":
        model_id = model_name  # OpenAI doesn't need a prefix
    else:
        model_id = f"{model_provider}:{model_name}"

    # Create the agent with proper model handling for pydantic-ai
    try:
        # Import model types directly to properly initialize the agent
        from pydantic_ai.models.anthropic import AnthropicModel
        from pydantic_ai.models.openai import OpenAIModel
        from pydantic_ai.models.gemini import GeminiModel
        from pydantic_ai.models.groq import GroqModel
        from pydantic_ai.models.mistral import MistralModel
        
        # Create the appropriate model object based on provider
        if model_provider == "anthropic":
            model_obj = AnthropicModel(model_name)
        elif model_provider == "openai":
            model_obj = OpenAIModel(model_name)
        elif model_provider == "google":
            model_obj = GeminiModel(model_name)
        elif model_provider == "groq":
            model_obj = GroqModel(model_name)
        elif model_provider == "mistral":
            model_obj = MistralModel(model_name)
        else:
            # For unknown providers, fall back to string format
            model_obj = model_id
        
        # Create the agent with proper model object, using different approach
        # depending on type to handle pydantic-ai's type requirements
        if isinstance(model_obj, str):
            # For string model IDs, we need to create a proper model object
            # Since we can't directly pass a string to Agent's model parameter
            from pydantic_ai.models import Model
            
            # Use a constructor approach that works with the type system
            # Create a model instance that implements the Model protocol
            if model_provider == "anthropic":
                from pydantic_ai.models.anthropic import AnthropicModel
                model_obj = AnthropicModel(model_name)
            else:
                # For other providers, use a more generic approach
                from pydantic_ai.models.openai import OpenAIModel
                model_obj = OpenAIModel(model_name)
            
            # Now use the model object
            agent = Agent(
                model=model_obj,
                result_type=model_class,
                system_prompt=system_prompt,
                model_settings={"temperature": temperature},
                retries=2,  # Allow more retries for complex structures
            )
        else:
            # For model objects, use them directly
            agent = Agent(
                model=model_obj,
                result_type=model_class,
                system_prompt=system_prompt,
                model_settings={"temperature": temperature},
                retries=2,  # Allow more retries for complex structures
            )

        # Run the agent to parse the content
        logger.info(f"Parsing natural language content with {model_provider}:{model_name}")
        result = await agent.run(content)
        parsed_model = result.data

        # Add the original content to variables if the model has variables attribute
        # Use safer approach that checks type and handles attribute access
        from recipe_executor.models.recipe import Recipe
        if isinstance(parsed_model, Recipe):
            # We know Recipe model has variables field
            parsed_model.variables["_original_recipe"] = content
        # Otherwise, don't try to access variables

        return parsed_model

    except Exception as e:
        logger.error(f"Error parsing with LLM: {e}")
        raise ValueError(f"Failed to parse content as {model_class.__name__}: {e}")


def _get_parsing_system_prompt(model_class: Type[BaseModel]) -> str:
    """Get the system prompt for parsing based on model class."""
    # Start with a generic prompt
    prompt = f"""You are an expert system that converts natural language descriptions into structured {model_class.__name__} objects.

    Analyze the input carefully and extract all the necessary information to create a valid {model_class.__name__} instance.
    Be precise and only include information that is explicitly stated or can be reasonably inferred.
    
    The model should be complete, valid, and follow all the requirements of the {model_class.__name__} class.
    """

    # Add model-specific guidance for Recipe class
    if model_class.__name__ == "Recipe":
        prompt += """
        A recipe MUST always contain these required fields:
        - metadata: Contains name (required), description (optional), and other metadata fields
        - steps: An array of step objects that define the workflow (must have at least one step)

        Each step MUST have:
        - id: A unique identifier for the step
        - type: The type of step (like "llm_generate", "file_read", etc.)
        - Configuration for the specific step type
        
        Be thoughtful about variable names and ensure they are used consistently throughout the recipe.
        """

    # Add Schema example if helpful
    schema = model_class.model_json_schema()
    prompt += f"""

    JSON Schema for {model_class.__name__}:
    ```json
    {json.dumps(schema, indent=2)}
    ```
    
    Return a complete, valid instance based on the input description.
    """

    return prompt
