import logging
import time
from typing import Optional, Any

from recipe_executor.models import FileGenerationResult
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel


# Configure logging for this module
logger = logging.getLogger(__name__)

DEFAULT_MODEL_ID = "openai:gpt-4o"


def get_model(model_id: str) -> Any:
    """
    Initialize an LLM model based on the standardized model_id string.
    Expected format: 'provider:model_name'.

    Args:
        model_id (str): The model identifier in format 'provider:model_name'.

    Returns:
        A model instance corresponding to the specified provider and model.

    Raises:
        ValueError: If the model_id format is invalid or if the provider is unsupported.
    """
    if ":" not in model_id:
        raise ValueError(f"Invalid model_id format: {model_id}. Expected format 'provider:model_name'.")
    provider, model_name = model_id.split(":", 1)
    provider = provider.strip().lower()
    model_name = model_name.strip()

    if provider == "openai":
        return OpenAIModel(model_name)
    elif provider == "anthropic":
        return AnthropicModel(model_name)
    elif provider == "gemini":
        return GeminiModel(model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize an LLM agent with the specified model.

    Args:
        model_id (Optional[str]): The model identifier in format 'provider:model_name'. If None,
                                  defaults to 'openai:gpt-4o'.

    Returns:
        Agent[None, FileGenerationResult]: A configured agent ready to process LLM requests with structured output.
    """
    if model_id is None:
        model_id = DEFAULT_MODEL_ID

    model = get_model(model_id)

    # Define a default system prompt instructing the LLM to produce a JSON structured output
    system_prompt = (
        "You are an LLM that generates a JSON object for file generation. "
        "The JSON object must contain a key 'files' which is an array of file objects. "
        "Each file object should have a 'path' (string) and 'content' (string). "
        "Optionally, include a 'commentary' field with additional information."
    )

    agent = Agent(
        model=model,
        result_type=FileGenerationResult,
        system_prompt=system_prompt,
    )

    return agent


def call_llm(prompt: str, model: Optional[str] = None) -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
        prompt (str): The prompt string to be sent to the LLM.
        model (Optional[str]): The model identifier in format 'provider:model_name'.
                               If None, defaults to 'openai:gpt-4o'.

    Returns:
        FileGenerationResult: A structured result containing generated files and commentary.

    Raises:
        Exception: If the LLM call fails or result validation fails.
    """
    agent = get_agent(model)
    start_time = time.time()
    try:
        result = agent.run_sync(prompt)
    except Exception as e:
        logger.exception("LLM call failed for prompt: %s", prompt)
        raise e
    elapsed = time.time() - start_time
    logger.debug("LLM call completed in %.2f seconds", elapsed)
    return result.data
