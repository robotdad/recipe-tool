import logging
import time
from typing import Optional

from recipe_executor.models import FileGenerationResult

# Import the LLM model classes from pydantic_ai
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel


def get_model(model_id: str):
    """
    Initialize and return a model instance based on the standardized model identifier.

    Supported model_id formats:
        provider:model_name
        For Azure, it can also be: azure:model_name:deployment_name

    Supported providers: openai, anthropic, gemini, azure

    Args:
        model_id (str): the identifier for the model

    Returns:
        Instance of the appropriate model class

    Raises:
        ValueError: if model_id is improperly formatted or provider is not supported
    """
    parts = model_id.split(":")
    if len(parts) < 2:
        raise ValueError(f"Invalid model_id format: {model_id}")

    provider = parts[0].lower()

    if provider == "azure":
        # For Azure, expected formats: azure:model_name or azure:model_name:deployment_name
        if len(parts) == 3:
            model_name = parts[1]
            deployment_name = parts[2]
        elif len(parts) == 2:
            model_name = parts[1]
            deployment_name = model_name  # default deployment same as model name
        else:
            raise ValueError(f"Invalid azure model identifier: {model_id}")
        # Use azure-specific helper to get the model instance
        from recipe_executor.llm_utils.azure_openai import get_openai_model
        return get_openai_model(model_name=model_name, deployment_name=deployment_name)

    elif provider == "openai":
        model_name = parts[1]
        return OpenAIModel(model_name)

    elif provider == "anthropic":
        model_name = parts[1]
        return AnthropicModel(model_name)

    elif provider == "gemini":
        model_name = parts[1]
        return GeminiModel(model_name)

    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize and return an Agent configured with the given model identifier.

    Args:
        model_id (Optional[str]): The identifier for the model to use. Defaults to 'openai:gpt-4o'.

    Returns:
        Agent instance with result type FileGenerationResult.
    """
    if model_id is None:
        model_id = "openai:gpt-4o"
    model_instance = get_model(model_id)
    agent = Agent(model_instance, result_type=FileGenerationResult)
    return agent


def call_llm(prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = None) -> FileGenerationResult:
    """
    Call the LLM with the provided prompt and return a structured FileGenerationResult.

    Args:
        prompt (str): The prompt/query to send to the model.
        model (Optional[str]): The model identifier (e.g. "openai:gpt-4o"). Default is 'openai:gpt-4o'.
        logger (Optional[logging.Logger]): Logger to record debug/info. Defaults to a logger named "RecipeExecutor".

    Returns:
        FileGenerationResult: The validated output returned by the LLM

    Raises:
        Exception: Propagates any exceptions raised during the LLM call.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    if model is None:
        model = "openai:gpt-4o"

    logger.debug(f"LLM Request - Prompt: {prompt}, Model: {model}")

    agent = get_agent(model_id=model)
    start_time = time.time()
    try:
        result = agent.run_sync(prompt)
    except Exception as e:
        logger.error(f"LLM call failed with error: {e}")
        raise
    elapsed = time.time() - start_time
    logger.info(f"Model {model} responded in {elapsed:.2f} seconds")
    logger.debug(f"LLM Response: {result}")

    # Return only the structured data
    return result.data
