import logging
import os
import time
from typing import Optional

# Import Azure identity and AsyncAzureOpenAI if available
try:
    from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
except ImportError:
    DefaultAzureCredential = None
    ManagedIdentityCredential = None

try:
    from openai import AsyncAzureOpenAI
except ImportError:
    AsyncAzureOpenAI = None

# Import Agent from Pydantic AI and the FileGenerationResult for structured output
from pydantic_ai import Agent
from recipe_executor.models import FileGenerationResult


def get_model(model_id: str):
    """
    Initialize and return an LLM model based on a colon-separated identifier.
    Supported formats:
      - openai:model_name
      - anthropic:model_name
      - gemini:model_name
      - azure:model_name or azure:model_name:deployment_name
    """
    parts = model_id.split(":")
    if len(parts) < 2:
        raise ValueError("Invalid model identifier. Expected format 'provider:model_name[:deployment_name]'")
    
    provider = parts[0].lower()

    if provider == "openai":
        if len(parts) != 2:
            raise ValueError("Invalid format for OpenAI model. Expected 'openai:model_name'")
        from pydantic_ai.models.openai import OpenAIModel
        return OpenAIModel(parts[1])

    elif provider == "anthropic":
        if len(parts) != 2:
            raise ValueError("Invalid format for Anthropic model. Expected 'anthropic:model_name'")
        from pydantic_ai.models.anthropic import AnthropicModel
        return AnthropicModel(parts[1])

    elif provider == "gemini":
        if len(parts) != 2:
            raise ValueError("Invalid format for Gemini model. Expected 'gemini:model_name'")
        from pydantic_ai.models.gemini import GeminiModel
        return GeminiModel(parts[1])

    elif provider == "azure":
        # Azure supports either azure:model_name or azure:model_name:deployment_name, but deployment is handled via model parameter
        from pydantic_ai.models.openai import OpenAIModel
        from pydantic_ai.providers.azure import AzureProvider

        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("OPENAI_API_VERSION")
        if not azure_endpoint or not api_version:
            raise ValueError("Missing required environment variables: AZURE_OPENAI_ENDPOINT and OPENAI_API_VERSION")

        if len(parts) == 2:
            model_name = parts[1]
        elif len(parts) == 3:
            model_name = parts[1]  # deployment name provided as parts[2] is ignored because AzureProvider does not accept deployment_name
        else:
            raise ValueError("Invalid format for Azure model. Expected 'azure:model_name' or 'azure:model_name:deployment_name'")

        use_managed_identity = os.getenv("AZURE_USE_MANAGED_IDENTITY", "false").lower() == "true"
        if use_managed_identity:
            if DefaultAzureCredential is None:
                raise ImportError("azure-identity package is required for managed identity authentication")
            client_id = os.getenv("AZURE_MANAGED_IDENTITY_CLIENT_ID")
            if client_id:
                credential = ManagedIdentityCredential(client_id=client_id)
            else:
                credential = DefaultAzureCredential()

            if AsyncAzureOpenAI is None:
                raise ImportError("openai package with AsyncAzureOpenAI is required for Azure managed identity support")

            # Mandatory token scope for managed identity
            def get_bearer_token_provider():
                scope = "https://cognitiveservices.azure.com/.default"
                token = credential.get_token(scope)
                return token.token

            custom_client = AsyncAzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_version=api_version,
                azure_ad_token_provider=get_bearer_token_provider
            )
            provider_instance = AzureProvider(openai_client=custom_client)
        else:
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            if not api_key:
                raise ValueError("Missing environment variable AZURE_OPENAI_API_KEY for Azure authentication")
            provider_instance = AzureProvider(
                azure_endpoint=azure_endpoint,
                api_version=api_version,
                api_key=api_key
            )
        
        return OpenAIModel(model_name, provider=provider_instance)

    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initializes and returns an Agent configured with a standardized system prompt for file generation.
    Defaults to 'openai:gpt-4o' if no model_id is provided.
    """
    if model_id is None:
        model_id = "openai:gpt-4o"
    model = get_model(model_id)
    system_prompt = (
        "Generate a JSON object with exactly two keys: 'files' and 'commentary'. "
        "The 'files' key should be an array of objects, each with 'path' and 'content' properties. "
        "The 'commentary' field is optional. "
        "Return your output strictly in JSON format."
    )

    return Agent(
        model=model,
        result_type=FileGenerationResult,
        system_prompt=system_prompt,
        retries=3
    )


def call_llm(prompt: str, model: Optional[str] = None) -> FileGenerationResult:
    """
    Calls the LLM with the given prompt and optional model identifier, logging the execution time,
    and returns a FileGenerationResult. Basic error handling and retry logic is implemented.
    """
    logger = logging.getLogger("RecipeExecutor.LLM")
    logger.debug(f"LLM call started with prompt: {prompt}")
    start_time = time.time()
    try:
        agent_instance = get_agent(model)
        result = agent_instance.run_sync(prompt)
    except Exception as e:
        logger.error("Error during LLM call", exc_info=True)
        raise e
    elapsed = time.time() - start_time
    logger.debug(f"LLM call finished in {elapsed:.2f} seconds")
    logger.debug(f"LLM response: {result.data}")
    return result.data
