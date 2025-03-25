"""LLM generation executor function."""

import asyncio
import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Type

import yaml
from pydantic import BaseModel, Field, create_model
from pydantic_ai import Agent

from recipe_executor.constants import OutputFormat, StepType
from recipe_executor.context.simple_context import ExecutionContext
from recipe_executor.executors.registry import register_executor
from recipe_executor.models.base import FilesGenerationResult
from recipe_executor.models.step import RecipeStep
from recipe_executor.utils import logging as log_utils

logger = log_utils.get_logger("llm")


@register_executor(StepType.LLM_GENERATE)
async def execute_llm_generate(step: RecipeStep, context: ExecutionContext) -> Any:
    """Execute an LLM generation step."""
    if not step.llm_generate:
        raise ValueError(f"Missing llm_generate configuration for step {step.id}")

    config = step.llm_generate
    
    # Process prompt through template engine to handle liquid templates
    prompt = context.interpolate_variables(config.prompt)
    
    # Debug log the processed prompt to help with template debugging
    logger.debug(f"Processed prompt for step {step.id}:\n{'-'*40}\n{prompt}\n{'-'*40}")

    # Determine which model to use
    model_provider = "anthropic"
    model_name = config.model

    if context.recipe and context.recipe.model:
        model_provider = context.recipe.model.provider
        if not model_name:
            model_name = context.recipe.model.model_name

    if not model_name:
        model_name = "claude-3-7-sonnet-20250219"

    # Get the temperature
    temp = config.temperature
    if temp is None and context.recipe and context.recipe.model:
        temp = context.recipe.model.temperature

    # Get the system prompt
    system_prompt = None
    if (
        context.recipe
        and context.recipe.model
        and context.recipe.model.system_prompt
    ):
        system_prompt = context.interpolate_variables(
            context.recipe.model.system_prompt
        )

    # Check for cached result
    cache_dir = getattr(context, "cache_dir", None)
    cache_key = None
    if cache_dir:
        h = hashlib.md5()
        h.update(prompt.encode("utf-8"))
        if system_prompt:
            h.update(system_prompt.encode("utf-8"))
        h.update(str(config.output_format).encode("utf-8"))
        if config.structured_schema:
            h.update(json.dumps(config.structured_schema).encode("utf-8"))
        cache_key = h.hexdigest()
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")

        # Check if we have a cached result
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    cached_data = json.load(f)
                logger.info(f"Using cached result for step {step.id}")
                return cached_data.get("result")
            except Exception as e:
                logger.warning(f"Failed to load cached result: {e}")

    # Prepare message history if needed
    message_history = None
    if config.include_history:
        message_history = context.get_message_history(step.id)
    elif config.history_variable and context.get_variable(config.history_variable) is not None:
        history_var = context.get_variable(config.history_variable)
        # Check if history_var is a list and its items have the appropriate attributes
        if isinstance(history_var, list) and all(
            hasattr(msg, "role") and hasattr(msg, "content") for msg in history_var
        ):
            message_history = history_var

    # Handle structured output
    result_type: Type = str

    if config.output_format == OutputFormat.JSON:
        result_type = Dict[str, Any]
    elif config.output_format == OutputFormat.FILES:
        result_type = FilesGenerationResult
    elif config.output_format == OutputFormat.STRUCTURED:
        # Create a dynamic model from the schema
        schema = None

        if config.structured_schema:
            schema = config.structured_schema
        elif config.structured_schema_file:
            schema_file = context.interpolate_variables(
                config.structured_schema_file
            )
            try:
                with open(schema_file, "r") as f:
                    if schema_file.endswith(".json"):
                        schema = json.load(f)
                    elif schema_file.endswith((".yaml", ".yml")):
                        schema = yaml.safe_load(f)
                    else:
                        raise ValueError(
                            f"Unsupported schema file format: {schema_file}"
                        )
            except Exception as e:
                logger.error(f"Error loading schema file {schema_file}: {e}")
                raise

        if schema:
            result_type = await _create_dynamic_model(schema, context)
        else:
            # Default to Dict if no schema provided
            result_type = Dict[str, Any]

    # Set up timeout handling
    timeout = config.timeout
    if timeout is None and step.timeout:
        timeout = step.timeout
    if timeout is None and context.recipe and context.recipe.timeout:
        timeout = context.recipe.timeout

    # Get the agent
    agent = _get_agent(
        model_provider=model_provider,
        model_name=model_name,
        result_type=result_type,
        system_prompt=system_prompt,
        temp=temp,
    )

    # Log the LLM prompt at debug level
    log_utils.log_llm_prompt(model_name, prompt, step.id)

    # Run the agent with timeout if specified
    if timeout:
        try:
            result = await asyncio.wait_for(
                agent.run(
                    prompt,
                    message_history=message_history,
                ),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.error(
                f"LLM generation timed out after {timeout}s for step {step.id}"
            )
            raise TimeoutError(f"LLM generation timed out after {timeout}s")
    else:
        result = await agent.run(
            prompt,
            message_history=message_history,
        )

    # Log the model response at debug level
    if hasattr(result, "data"):
        # For structured data, convert to JSON string for logging
        if isinstance(result.data, (dict, list)):
            response_text = json.dumps(result.data, indent=2, default=str)
        else:
            response_text = str(result.data)
        log_utils.log_llm_response(model_name, response_text, step.id)

    # Store the message history
    context.set_message_history(step.id, result.new_messages())

    # Store the result in the cache if enabled
    if cache_key and cache_dir:
        try:
            with open(os.path.join(cache_dir, f"{cache_key}.json"), "w") as f:
                json.dump(
                    {
                        "prompt": prompt,
                        "system_prompt": system_prompt,
                        "result": result.data,
                    },
                    f,
                )
        except Exception as e:
            logger.warning(f"Failed to cache result: {e}")

    return result.data


# Helper functions moved to module level
def _get_agent(
    model_provider: str,
    model_name: str,
    result_type: Type,
    system_prompt: Optional[str] = None,
    temp: Optional[float] = None,
) -> Agent:
    """Get an agent for the specified model."""
    # Verify API key before creating agent
    from recipe_executor.utils.authentication import AuthManager
    
    auth_manager = AuthManager()
    is_valid, error_message = auth_manager.verify_api_key(model_provider)
    
    if not is_valid:
        error_msg = f"Cannot create agent: {error_message}"
        logger.error(error_msg)
        instructions = auth_manager.get_api_key_instructions(model_provider)
        logger.info(f"API key setup instructions: {instructions}")
        raise ValueError(error_msg)
    
    # Import model types directly to properly initialize the agent
    from pydantic_ai.models.anthropic import AnthropicModel
    from pydantic_ai.models.openai import OpenAIModel
    from pydantic_ai.models.gemini import GeminiModel
    from pydantic_ai.models.groq import GroqModel
    from pydantic_ai.models.mistral import MistralModel
    
    # Set up model settings
    model_settings = {"temperature": temp if temp is not None else 0.1}
    
    # Create the appropriate model object based on provider
    try:
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
            # For unknown providers, format a model string ID
            model_id = f"{model_provider}:{model_name}"
            model_obj = model_id
        
        # Create the agent with proper model object
        agent_kwargs = {
            "model": model_obj,
            "result_type": result_type,
            "model_settings": model_settings,
        }
        
        # Only add system_prompt if it's not None
        if system_prompt is not None:
            agent_kwargs["system_prompt"] = system_prompt
        
        # Create the agent
        agent = Agent(**agent_kwargs)
        return agent
            
    except Exception as e:
        # Enhance error message with more context
        logger.error(f"Error creating agent: {e}")
        raise ValueError(f"Failed to create agent for {model_provider}:{model_name}: {str(e)}")


async def _create_dynamic_model(
    schema: Dict[str, Any], context: ExecutionContext
) -> Type[BaseModel]:
    """Create a Pydantic model dynamically from a schema."""
    # Extract the fields from the schema
    fields = {}
    for field_name, field_def in schema.get("properties", {}).items():
        field_type = field_def.get("type")
        description = field_def.get("description", "")

        if field_type == "string":
            fields[field_name] = (str, Field(description=description))
        elif field_type == "integer":
            fields[field_name] = (int, Field(description=description))
        elif field_type == "number":
            fields[field_name] = (float, Field(description=description))
        elif field_type == "boolean":
            fields[field_name] = (bool, Field(description=description))
        elif field_type == "array":
            items = field_def.get("items", {})
            item_type = items.get("type", "string")
            if item_type == "string":
                fields[field_name] = (List[str], Field(description=description))
            elif item_type == "integer":
                fields[field_name] = (List[int], Field(description=description))
            elif item_type == "number":
                fields[field_name] = (List[float], Field(description=description))
            elif item_type == "boolean":
                fields[field_name] = (List[bool], Field(description=description))
            else:
                fields[field_name] = (List[Any], Field(description=description))
        elif field_type == "object":
            # For now, treat nested objects as dictionaries
            fields[field_name] = (Dict[str, Any], Field(description=description))
        else:
            # Default to Any for unknown types
            fields[field_name] = (Any, Field(description=description))

    # Create the model with the extracted fields
    model_name = schema.get("title", "DynamicModel")
    model = create_model(model_name, **fields)
    return model
