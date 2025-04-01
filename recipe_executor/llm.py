import logging
import time
from typing import Optional, Any

# The llm component provides a unified interface to interact with different LLM providers.
# Supported providers: openai, anthropic, gemini.


def get_model(model_id: str) -> Any:
    """
    Initialize an LLM model based on the standardized model_id "provider:model_name".

    Args:
        model_id (str): The model identifier, e.g., "openai:gpt-4o", "anthropic:claude-3-5-sonnet-latest", or "gemini:gemini-pro".

    Returns:
        A model instance appropriate for the provider.

    Raises:
        ValueError: If the model_id format is invalid or the provider is unsupported.
    """
    parts = model_id.split(":")
    if len(parts) != 2:
        raise ValueError("Invalid model_id format. Expected format 'provider:model_name'.")

    provider, model_name = parts
    provider = provider.lower()

    if provider == "openai":
        try:
            from pydantic_ai.models.openai import OpenAIModel
        except ImportError as e:
            raise ImportError("OpenAI model support is not available. Ensure the required packages are installed.") from e
        return OpenAIModel(model_name)
    elif provider == "anthropic":
        try:
            from pydantic_ai.models.anthropic import AnthropicModel
        except ImportError as e:
            raise ImportError("Anthropic model support is not available. Ensure the required packages are installed.") from e
        return AnthropicModel(model_name)
    elif provider == "gemini":
        try:
            from pydantic_ai.models.gemini import GeminiModel
        except ImportError as e:
            raise ImportError("Gemini model support is not available. Ensure the required packages are installed.") from e
        return GeminiModel(model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_agent(model_id: Optional[str] = None) -> Any:
    """
    Initialize an LLM agent with the specified model.

    If model_id is not provided, defaults to 'openai:gpt-4o'.

    Returns:
        Agent: A configured Agent instance ready to process LLM requests.
    """
    if model_id is None:
        model_id = "openai:gpt-4o"
    model = get_model(model_id)

    try:
        from recipe_executor.models import FileGenerationResult
    except ImportError as e:
        raise ImportError("FileGenerationResult model not found. Ensure that recipe_executor/models.py is available.") from e

    try:
        from pydantic_ai import Agent
    except ImportError as e:
        raise ImportError("PydanticAI Agent not available. Please install pydantic-ai.") from e

    # Create the Agent with the given model and expected result type.
    agent = Agent(model=model, result_type=FileGenerationResult)
    return agent


def call_llm(prompt: str, model: Optional[str] = None) -> Any:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
        prompt (str): The prompt to send to the LLM.
        model (Optional[str]): The model identifier in the format 'provider:model_name'. If None, defaults to 'openai:gpt-4o'.

    Returns:
        FileGenerationResult: Structured result containing generated files and optional commentary.

    Raises:
        Exception: If the LLM call fails or result validation fails.
    """
    agent = get_agent(model)
    start_time = time.time()
    try:
        result = agent.run_sync(prompt)
    except Exception as e:
        logging.exception("LLM call failed")
        raise
    elapsed = time.time() - start_time
    logging.debug(f"LLM call took {elapsed:.2f} seconds.")
    return result.data
