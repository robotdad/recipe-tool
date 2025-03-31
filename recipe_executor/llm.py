import logging
import time
from typing import Optional

from pydantic_ai import Agent

from recipe_executor.models import FileGenerationResult


def get_model(model_id: str):
    """
    Initialize and return an LLM model based on a standardized model_id string.
    Expected format: "provider:model_name"

    Supported providers:
      - openai
      - anthropic
      - gemini

    Args:
        model_id (str): The identifier of the model.

    Raises:
        ValueError: If the model_id format is invalid or if the provider is unsupported.

    Returns:
        An instance of the corresponding LLM model.
    """
    try:
        provider, model_name = model_id.split(":", 1)
    except ValueError as e:
        raise ValueError("Invalid model_id format. Expected format 'provider:model_name'.") from e

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
    Creates and returns a configured Agent for LLM interactions.

    If no model_id is provided, a default of "openai:gpt-4o" is used.

    The agent is configured with:
      - A default system prompt instructing the LLM to output a JSON object with exactly two keys: 'files' and 'commentary'
      - 3 retries in case of transient errors
      - Result type validation using FileGenerationResult

    Args:
        model_id (Optional[str]): The model identifier (format 'provider:model_name').

    Returns:
        A configured Agent instance ready to be used to call the LLM.
    """
    if model_id is None:
        model_id = "openai:gpt-4o"
    model = get_model(model_id)
    system_prompt = (
        "Generate a JSON object with exactly two keys: 'files' and 'commentary'. "
        "The 'files' key should be an array of objects, each with 'path' and 'content' properties. "
        "Return your output strictly in JSON format."
    )
    return Agent(model=model, result_type=FileGenerationResult, retries=3, system_prompt=system_prompt)


def call_llm(prompt: str, model: Optional[str] = None) -> FileGenerationResult:
    """
    Calls the LLM with a given prompt and returns a structured FileGenerationResult.

    This function logs the prompt, measures the execution time, initializes the LLM agent,
    and returns the validated response data. In case of errors, it logs detailed information
    before re-raising the exception.

    Args:
        prompt (str): The prompt to send to the LLM.
        model (Optional[str]): The model identifier in the format 'provider:model_name'.
                               If not provided, a default is used.

    Returns:
        FileGenerationResult: A structured result containing generated files and commentary.
    """
    logger = logging.getLogger("RecipeExecutor")
    logger.debug(f"LLM call initiated with prompt: {prompt}")
    start_time = time.time()

    try:
        agent = get_agent(model)
        result = agent.run_sync(prompt)
    except Exception as e:
        logger.error("Error during LLM call", exc_info=True)
        raise e

    elapsed = time.time() - start_time
    logger.debug(f"LLM call completed in {elapsed:.2f} seconds")
    logger.debug(f"LLM response: {result}")

    return result.data
