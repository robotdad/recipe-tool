import logging
import time
from typing import Optional

from pydantic_ai import Agent
from recipe_executor.models import FileGenerationResult


def get_model(model_id: str):
    """
    Initialize and return an LLM model based on the standardized model_id string.
    Expected formats:
      - openai:model_name
      - anthropic:model_name
      - gemini:model_name
      - azure:model_name:deployment_name
    """
    try:
        parts = model_id.split(":")
    except Exception as e:
        raise ValueError("Invalid model_id format. Expected a colon-separated string.") from e

    provider = parts[0].lower()
    if provider == "azure":
        if len(parts) != 3:
            raise ValueError("Invalid azure model_id format. Expected 'azure:model_name:deployment_name'.")
        model_name = parts[1]
        deployment_name = parts[2]
        # Import the Azure OpenAI model class from pydantic_ai (assumed to exist)
        from pydantic_ai.models.azure_openai import AzureOpenAIModel
        return AzureOpenAIModel(model_name, deployment_name=deployment_name)
    elif provider == "openai":
        if len(parts) != 2:
            raise ValueError("Invalid openai model_id format. Expected 'openai:model_name'.")
        model_name = parts[1]
        from pydantic_ai.models.openai import OpenAIModel
        return OpenAIModel(model_name)
    elif provider == "anthropic":
        if len(parts) != 2:
            raise ValueError("Invalid anthropic model_id format. Expected 'anthropic:model_name'.")
        model_name = parts[1]
        from pydantic_ai.models.anthropic import AnthropicModel
        return AnthropicModel(model_name)
    elif provider == "gemini":
        if len(parts) != 2:
            raise ValueError("Invalid gemini model_id format. Expected 'gemini:model_name'.")
        model_name = parts[1]
        from pydantic_ai.models.gemini import GeminiModel
        return GeminiModel(model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Creates and returns an Agent configured with a given model.
    If model_id is not provided, defaults to "openai:gpt-4o".
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
    Calls the LLM with a given prompt, logs execution time, and returns a structured FileGenerationResult.

    Args:
      prompt: The prompt to be sent to the LLM.
      model: Optional model identifier (format provider:model_name or azure:model:deployment).
              If not provided, defaults to "openai:gpt-4o".

    Returns:
      A FileGenerationResult object containing generated files and commentary.
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
