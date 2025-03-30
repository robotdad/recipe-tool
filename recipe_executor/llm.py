import logging
import time
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.models import Model
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel

from recipe_executor.models import FileGenerationResult, FileSpec

logger = logging.getLogger("RecipeExecutor")


def get_model(model_id: str) -> Model:
    """
    Initializes the LLM model based on the provided model_id.
    The model_id should be in the format 'provider:model_name'.
    Supported providers: 'anthropic', 'gemini', 'openai'.

    Returns:
        Model: A configured model instance for the specified provider.
    """
    try:
        provider, model_name = model_id.split(":", 1)
    except ValueError:
        message = "Invalid model_id format. Expected 'provider:model_name'."
        logger.error(message)
        raise ValueError(message)

    if provider == "anthropic":
        logger.debug(f"Using Anthropic model: {model_name}")
        return AnthropicModel(model_name=model_name)
    elif provider == "gemini":
        logger.debug(f"Using Gemini model: {model_name}")
        return GeminiModel(model_name=model_name)
    elif provider == "openai":
        logger.debug(f"Using OpenAI model: {model_name}")
        return OpenAIModel(model_name=model_name)
    else:
        message = f"Unknown provider '{provider}'. Supported providers are 'anthropic', 'gemini', and 'openai'."
        logger.error(message)
        raise ValueError(message)


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initializes the LLM agent with the specified model.

    If no model_id is provided, defaults to 'openai:gpt-4o'.
    The agent is configured with:
      - A system prompt instructing it to generate JSON with exactly two keys: 'files' and 'commentary'.
      - Retry logic up to 3 times.
      - Return type validation using FileGenerationResult.

    Returns:
        Agent[None, FileGenerationResult]: A configured agent ready to handle LLM requests.
    """
    if model_id is None:
        model_id = "openai:gpt-4o"
        logger.debug(f"No model_id provided. Using default model_id: {model_id}")

    model = get_model(model_id)
    logger.debug(f"Initializing LLM agent with model: {model.model_name}")

    system_prompt = (
        "You are a file generation assistant. Given a specification, generate a JSON object with exactly two keys: 'files' and 'commentary'. "
        "The 'files' key should be a list of file objects, each containing 'path' and 'content'. "
        "Ensure that in any code you include, backslashes are properly escaped (\\ instead of \). "
        "All special characters in string values must be properly JSON-escaped. Do not include any extra text."
    )

    try:
        agent = Agent(
            model=model,
            system_prompt=system_prompt,
            retries=3,
            result_type=FileGenerationResult,
        )
        logger.debug("LLM agent initialized successfully.")
        return agent
    except Exception as e:
        message = f"Failed to initialize LLM agent: {e}"
        logger.error(message, exc_info=True)
        raise e


def call_llm(prompt: str, model: Optional[str] = None) -> FileGenerationResult:
    """
    Calls the LLM with the provided prompt and returns a structured FileGenerationResult.

    Behavior:
      - Logs the request prompt.
      - Initializes the appropriate agent using the provided or default model.
      - Measures and logs the response time.
      - Handles errors gracefully, returning a dummy FileGenerationResult in case of failure.

    Args:
        prompt (str): The instruction prompt for the LLM.
        model (Optional[str]): Optional model_id in 'provider:model_name' format.

    Returns:
        FileGenerationResult: Contains a list of generated files and optional commentary.
    """
    logger.debug(f"LLM request prompt: {prompt}")
    agent = get_agent(model_id=model)

    try:
        start_time = time.perf_counter()
        result = agent.run_sync(prompt)
        elapsed_time = time.perf_counter() - start_time
        logger.debug(f"LLM response received in {elapsed_time:.2f} seconds: {result.data}")
        return result.data
    except Exception as e:
        error_message = f"LLM call failed: {e}"
        logger.error(error_message, exc_info=True)
        dummy_file = FileSpec(path="generated/hello.py", content='print("Hello, Test!")')
        return FileGenerationResult(files=[dummy_file], commentary="Dummy LLM output due to error")
