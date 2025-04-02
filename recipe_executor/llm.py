import logging
import time
from typing import Optional

from recipe_executor.models import FileGenerationResult

# Import LLM model classes from pydantic_ai package
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel


def get_model(model_id: str):
    """
    Initialize and return an LLM model instance based on a standardized model identifier format.

    Supported model id formats:
      - openai:model_name
      - anthropic:model_name
      - gemini:model_name
      - azure:model_name or azure:model_name:deployment_name

    Raises:
        ValueError: for an improperly formatted model_id or unsupported provider.
    """
    parts = model_id.split(":")
    if len(parts) < 2:
        raise ValueError(f"Invalid model identifier: {model_id}")

    provider = parts[0].lower()

    if provider == "openai":
        model_name = parts[1]
        return OpenAIModel(model_name)
    elif provider == "anthropic":
        model_name = parts[1]
        return AnthropicModel(model_name)
    elif provider == "gemini":
        model_name = parts[1]
        return GeminiModel(model_name)
    elif provider == "azure":
        # For Azure, allowed formats are: azure:model_name or azure:model_name:deployment_name
        if len(parts) == 2:
            model_name = parts[1]
            deployment_name = model_name  # Default deployment name is same as model name
        elif len(parts) == 3:
            model_name = parts[1]
            deployment_name = parts[2]
        else:
            raise ValueError(f"Invalid Azure model identifier: {model_id}")
        # Import the azure-specific function to get the model
        from recipe_executor.llm_utils.azure_openai import get_openai_model
        return get_openai_model(model_name=model_name, deployment_name=deployment_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize and return an Agent configured with the specified model identifier.

    If model_id is not specified, it defaults to 'openai:gpt-4o'.

    Returns:
        Agent instance with the result type set to FileGenerationResult.
    """
    if model_id is None:
        model_id = "openai:gpt-4o"
    model_instance = get_model(model_id)
    agent = Agent(model_instance, result_type=FileGenerationResult)
    return agent


def call_llm(prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = None) -> FileGenerationResult:
    """
    Send a prompt to the LLM and return the validated FileGenerationResult.

    Args:
        prompt (str): The prompt/query to send to the LLM.
        model (Optional[str]): The LLM model identifier in the format 'provider:model_name' (or for Azure: 'azure:model_name[:deployment_name]').
                                Defaults to 'openai:gpt-4o' if not provided.
        logger (Optional[logging.Logger]): Logger instance to log debug and info messages. If not specified, a default logger named 'RecipeExecutor' is used.

    Returns:
        FileGenerationResult: The structured result produced by the LLM.

    Raises:
        Exception: Propagates any exceptions encountered during the LLM call with appropriate logging.
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

    # Return only the structured data from the result
    return result.data
