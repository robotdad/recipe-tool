import logging
import time
from typing import Optional

from pydantic_ai import Agent

from recipe_executor.models import FileGenerationResult


def get_model(model_id: str):
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider:model_name'.

    Supported providers:
        - openai: uses OpenAIModel
        - anthropic: uses AnthropicModel
        - gemini: uses GeminiModel

    Raises:
        ValueError: If model_id format is invalid or if the provider is unsupported.
    """
    try:
        provider, model_name = model_id.split(":", 1)
    except ValueError as e:
        raise ValueError("Invalid model_id format; expected 'provider:model_name'.") from e

    provider = provider.lower()
    if provider == "openai":
        from pydantic_ai.models.openai import OpenAIModel

        return OpenAIModel(model_name)
    elif provider == "anthropic":
        from pydantic_ai.models.anthropic import AnthropicModel

        return AnthropicModel(model_name)
    elif provider == "gemini":
        from pydantic_ai.models.gemini import GeminiModel

        return GeminiModel(model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize an LLM agent with the specified model.

    If no model_id is provided, defaults to 'openai:gpt-4o'.

    The agent is configured with:
      - A default model
      - A system prompt instructing it to generate a JSON output with exactly two keys: 'files' and 'commentary'
      - Retry logic (set to at least 3 retries)
      - Result type validation using FileGenerationResult

    Returns:
        A configured Agent ready to process LLM requests.
    """
    if model_id is None:
        model_id = "openai:gpt-4o"

    model_instance = get_model(model_id)
    system_prompt = (
        "Generate a JSON object with exactly two keys: 'files' and 'commentary'. "
        "The 'files' key should be an array of file objects, each with 'path' and 'content'."
    )

    return Agent(model=model_instance, result_type=FileGenerationResult, retries=3, system_prompt=system_prompt)


def call_llm(prompt: str, model: Optional[str] = None) -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    This function logs the request prompt and timing information, initializes the LLM agent
    with the specified (or default) model, and calls the agent synchronously to generate a result.

    In case of an error, detailed information is logged before re-raising the exception.

    Args:
        prompt (str): The prompt string to be sent to the LLM.
        model (Optional[str]): The model identifier in the format 'provider:model_name'. If None, defaults to 'openai:gpt-4o'.

    Returns:
        FileGenerationResult: The structured result containing generated files and commentary.
    """
    logger = logging.getLogger("RecipeExecutor")
    logger.debug(f"LLM call initiated with prompt: {prompt}")
    start_time = time.time()

    try:
        agent = get_agent(model)
        result = agent.run_sync(prompt)
    except Exception:
        logger.error("Error during LLM call", exc_info=True)
        raise

    elapsed = time.time() - start_time
    logger.debug(f"LLM call completed in {elapsed:.2f} seconds")
    logger.debug(f"LLM response: {result}")

    return result.data
