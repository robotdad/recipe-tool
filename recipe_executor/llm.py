import logging
import time
from typing import Optional, Union

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel

# Import our structured result models
from recipe_executor.models import FileGenerationResult


# The function get_model initializes the appropriate LLM model based on a standardized model id
# Format: 'provider:model_name' or 'provider:model_name:deployment_name' (for Azure OpenAI)

def get_model(model_id: str) -> Union[OpenAIModel, AnthropicModel, GeminiModel]:
    """
    Initialize an LLM model based on a standardized model_id string.

    Expected format:
      - For OpenAI:      "openai:model_name"
      - For Anthropic:   "anthropic:model_name"
      - For Gemini:      "gemini:model_name"
      - For Azure OpenAI: "azure:model_name" or "azure:model_name:deployment_name"

    Args:
        model_id (str): The model identifier in the format specified.

    Returns:
        An instance of the appropriate model class.

    Raises:
        ValueError: If the model_id format is invalid or provider unsupported.
    """
    parts = model_id.split(":")
    if len(parts) < 2:
        raise ValueError("Invalid model_id format. Expected 'provider:model_name' at minimum.")

    provider = parts[0].lower()
    model_name = parts[1]

    if provider == "azure":
        # For Azure OpenAI, deployment_name may be provided; if not, default deployment equals model_name
        deployment_name = model_name if len(parts) == 2 else parts[2]
        try:
            # Dynamically import the azure openai model initializer
            from recipe_executor.llm_utils.azure_openai import get_openai_model as get_azure_openai_model
        except ImportError as e:
            raise ImportError("Azure OpenAI support is not available. Ensure llm_utils/azure_openai.py exists and is accessible.") from e
        return get_azure_openai_model(model_name, deployment_name)
    elif provider == "openai":
        return OpenAIModel(model_name)
    elif provider == "anthropic":
        return AnthropicModel(model_name)
    elif provider == "gemini":
        return GeminiModel(model_name)
    else:
        raise ValueError(f"Unsupported model provider: {provider}")



def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize an LLM agent with the specified model using structured output.

    Args:
        model_id (Optional[str]): Model identifier in format 'provider:model_name'.
                                    If None, defaults to 'openai:gpt-4o'.

    Returns:
        Agent[None, FileGenerationResult]: A configured Agent ready to process LLM requests.
    """
    if not model_id:
        model_id = "openai:gpt-4o"
    model_instance = get_model(model_id)
    agent = Agent(model_instance, result_type=FileGenerationResult)
    return agent



def call_llm(prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = None) -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
        prompt (str): The prompt to send to the LLM.
        model (Optional[str]): The model identifier in the format 'provider:model_name' (or with deployment for Azure).
                               If None, defaults to 'openai:gpt-4o'.
        logger (Optional[logging.Logger]): Logger instance; if None, a default logger named "RecipeExecutor" is used.

    Returns:
        FileGenerationResult: The structured result containing files and commentary.

    Raises:
        Exception: If model configuration is invalid or the LLM call fails.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    if not model:
        model = "openai:gpt-4o"

    agent = get_agent(model)

    logger.debug(f"LLM Request Payload: prompt={prompt}, model={model}")
    start_time = time.time()
    try:
        result = agent.run_sync(prompt)
    except Exception as e:
        logger.exception(f"LLM call failed for model {model} with prompt: {prompt}")
        raise e
    elapsed = time.time() - start_time
    logger.info(f"Model '{model}' executed in {elapsed:.2f} seconds")
    logger.debug(f"LLM Response Payload: {result.all_messages()}")

    # Return the result data (structured FileGenerationResult)
    return result.data
