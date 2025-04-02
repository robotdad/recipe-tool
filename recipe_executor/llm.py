import os
import logging
from typing import Optional, Union

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.azure import AzureProvider

from recipe_executor.models import FileGenerationResult


def get_model(model_id: Optional[str]) -> Union[OpenAIModel, AnthropicModel, GeminiModel]:
    """
    Initialize and return the appropriate LLM model instance based on the standardized model identifier.
    Expected formats:
        provider:model_name
        For Azure OpenAI: azure:model_name or azure:model_name:deployment_name
        For other providers, simply use provider:model_name
    """
    if not model_id:
        model_id = "openai:gpt-4o"
    parts = model_id.split(":")
    if len(parts) < 2:
        raise ValueError("Invalid model_id format. Expected 'provider:model_name' (and optionally ':deployment')")
    provider_str = parts[0].lower()
    model_name = parts[1]

    if provider_str == "azure":
        # For Azure OpenAI, optionally a deployment name may be provided but we ignore it
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not azure_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable not set for Azure OpenAI.")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        use_managed_identity = os.getenv("AZURE_USE_MANAGED_IDENTITY", "false").lower() == "true"
        if not azure_api_key and not use_managed_identity:
            raise ValueError("AZURE_OPENAI_API_KEY must be set if not using managed identity.")
        # For Azure, we use the OpenAIModel wrapper but with an AzureProvider
        return OpenAIModel(
            model_name,
            provider=AzureProvider(
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                api_key=azure_api_key
            )
        )
    elif provider_str == "openai":
        return OpenAIModel(model_name)
    elif provider_str == "anthropic":
        return AnthropicModel(model_name)
    elif provider_str in ["gemini", "google-gla", "google-vertex"]:
        return GeminiModel(model_name)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_str}")


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize and return an LLM agent configured with the specified model.

    Args:
        model_id (Optional[str]): The model identifier in the format 'provider:model_name'.
            Defaults to 'openai:gpt-4o' if not provided.

    Returns:
        Agent configured to produce a FileGenerationResult.
    """
    model = get_model(model_id)
    agent = Agent(model, result_type=FileGenerationResult)
    return agent


def call_llm(prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = None) -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
        prompt (str): The prompt string to be sent to the LLM.
        model (Optional[str]): The model identifier in the format 'provider:model_name' (or with deployment for Azure).
            If None, defaults to 'openai:gpt-4o'.
        logger (Optional[logging.Logger]): Logger instance. If not provided, a default logger named 'RecipeExecutor' is used.

    Returns:
        FileGenerationResult: The result of the LLM call containing generated file specs and optional commentary.

    Raises:
        Exception: Propagates any errors during the LLM call.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")
    logger.info(f"Calling LLM with model: {model if model else 'openai:gpt-4o'}")
    try:
        agent = get_agent(model)
        logger.debug(f"Agent initialized with model: {agent.model}")
        result = agent.run_sync(prompt)
        logger.info(f"LLM call successful. Model: {agent.model}")
        return result.data
    except Exception as e:
        logger.exception("LLM call failed")
        raise
