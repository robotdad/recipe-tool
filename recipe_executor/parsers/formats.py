"""Format-specific adapters for loading recipes."""

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar, Union, cast

import yaml
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.models.mistral import MistralModel

from recipe_executor.constants import DEFAULT_MODEL_NAME, DEFAULT_MODEL_PROVIDER, DEFAULT_TEMPERATURE
from recipe_executor.utils import logging as log_utils

logger = log_utils.get_logger("formats")

# Generic type for model parsing
T = TypeVar("T", bound=BaseModel)


def load_from_yaml(content: str, model_class: Type[T]) -> T:
    """
    Load a recipe from YAML content.
    
    Args:
        content: YAML content to parse
        model_class: Pydantic model class to validate against
        
    Returns:
        Validated model instance
        
    Raises:
        ValueError: If parsing fails
    """
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
    """
    Load a recipe from JSON content.
    
    Args:
        content: JSON content to parse
        model_class: Pydantic model class to validate against
        
    Returns:
        Validated model instance
        
    Raises:
        ValueError: If parsing fails
    """
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
    """
    Extract structured content from markdown code blocks or YAML frontmatter.
    
    Args:
        markdown: Markdown content with potential code blocks or frontmatter
        
    Returns:
        Extracted structured data or None if not found
    """
    # First try to extract YAML frontmatter (between --- markers)
    frontmatter_match = re.search(r"^---\n(.*?)\n---", markdown, re.DOTALL)
    if frontmatter_match:
        try:
            yaml_content = frontmatter_match.group(1)
            logger.debug(f"Found YAML frontmatter: {yaml_content[:100]}...")
            return yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML frontmatter: {e}")

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

    logger.debug("No structured content found in markdown")
    return None


def get_llm_model(model_name: str, model_provider: str) -> Union[AnthropicModel, OpenAIModel, GeminiModel, GroqModel, MistralModel]:
    """
    Get the appropriate model class for a provider.
    
    Args:
        model_name: Name of the model
        model_provider: Provider of the model
        
    Returns:
        A model object for pydantic-ai
    """
    if model_provider.lower() == "anthropic":
        return AnthropicModel(model_name)
    elif model_provider.lower() == "openai":
        return OpenAIModel(model_name)
    elif model_provider.lower() == "google":
        return GeminiModel(model_name)
    elif model_provider.lower() == "groq":
        return GroqModel(model_name)
    elif model_provider.lower() == "mistral":
        return MistralModel(model_name)
    else:
        # For unknown providers, default to OpenAI
        logger.warning(f"Unknown provider: {model_provider}, defaulting to OpenAI")
        return OpenAIModel(model_name)


async def parse_natural_language(
    content: str, 
    model_class: Type[T], 
    model_name: str = DEFAULT_MODEL_NAME, 
    model_provider: str = DEFAULT_MODEL_PROVIDER, 
    temperature: float = DEFAULT_TEMPERATURE
) -> T:
    """
    Parse natural language content into a structured model.
    
    Args:
        content: Natural language content to parse
        model_class: Pydantic model class to parse into
        model_name: Name of the model to use
        model_provider: Provider of the model
        temperature: Temperature setting for generation
        
    Returns:
        Parsed and validated model instance
        
    Raises:
        ValueError: If parsing fails
    """
    # Create a system prompt tailored to the model class
    system_prompt = _get_parsing_system_prompt(model_class)

    try:
        # Create the appropriate model object
        model_obj = get_llm_model(model_name, model_provider)
        
        # Create the agent
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
        from recipe_executor.models.recipe import Recipe
        if isinstance(parsed_model, Recipe) and hasattr(parsed_model, "variables"):
            parsed_model.variables["_original_recipe"] = content

        return parsed_model

    except Exception as e:
        logger.error(f"Error parsing with LLM: {e}")
        raise ValueError(f"Failed to parse content as {model_class.__name__}: {e}")


def _get_parsing_system_prompt(model_class: Type[BaseModel]) -> str:
    """
    Get the system prompt for parsing based on model class.
    
    Args:
        model_class: The pydantic model class to create a prompt for
        
    Returns:
        System prompt for the LLM
    """
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
        - type: The type of step (like "llm", "file", "template", "python", "validator", "chain", "conditional", "parallel", "json", "api", "input")
        - config: A configuration object specific to the step type

        Common step types include:
        - "llm": For LLM generation (config needs: model, provider, prompt, output_var)
        - "file": For file operations (config needs: operation, path, output_var)
        - "template": For string templates (config needs: template, output_var)
        - "python": For executing Python code (config needs: code, output_var)
        
        Be thoughtful about variable names and ensure they are used consistently throughout the recipe.
        
        IMPORTANT: When facing a markdown file with a recipe, pay careful attention to the YAML frontmatter between the '---' markers. This contains the recipe definition that should be used directly.
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


def load_recipe_file(file_path: str, model_class: Type[T]) -> T:
    """
    Load a recipe from a file with automatic format detection.
    
    Args:
        file_path: Path to the recipe file
        model_class: Pydantic model class to validate against
        
    Returns:
        Validated model instance
        
    Raises:
        ValueError: If loading fails
        FileNotFoundError: If the file doesn't exist
    """
    # Check if file exists
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Recipe file not found: {file_path}")
        
    # Read the file content
    with open(file_path, "r") as f:
        content = f.read()
        
    # Determine format based on extension
    file_ext = path.suffix.lower()
    
    if file_ext in (".yaml", ".yml"):
        return load_from_yaml(content, model_class)
    elif file_ext == ".json":
        return load_from_json(content, model_class)
    elif file_ext == ".md":
        # Try to extract structured content from markdown
        structured_data = extract_structured_content(content)
        if structured_data:
            return model_class.model_validate(structured_data)
        else:
            # If no structured content, treat as natural language
            # This will be handled by the caller since it requires async
            raise ValueError("Markdown file contains no structured content and requires async parsing")
    else:
        # For other formats, assume it's natural language
        # This will be handled by the caller since it requires async
        raise ValueError(f"Unsupported file extension: {file_ext}")