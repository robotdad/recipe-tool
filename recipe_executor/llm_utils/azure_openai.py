import os
import logging
from typing import Optional

import openai
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Import PydanticAI models for OpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


def get_openai_model(
    model_name: str,
    deployment_name: Optional[str] = None,
    logger: Optional[logging.Logger] = None
) -> OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance for Azure OpenAI, configured from environment variables.

    Environment Variables:
      - AZURE_OPENAI_ENDPOINT: Required. The endpoint for the Azure OpenAI resource.
      - AZURE_OPENAI_API_VERSION: Optional. Defaults to '2024-07-01-preview'.
      - AZURE_USE_MANAGED_IDENTITY: Set to 'true' to use Managed Identity authentication.
      - AZURE_MANAGED_IDENTITY_CLIENT_ID: Optional. Client ID for a user-assigned managed identity.
      - AZURE_OPENAI_API_KEY: Required if not using managed identity.

    Args:
      model_name: The name of the model to use (e.g. "gpt-4o").
      deployment_name: Optional deployment name; defaults to model_name if not provided.
      logger: An optional logger to log creation info.

    Returns:
      An instance of OpenAIModel configured for Azure OpenAI.

    Raises:
      ValueError: If critical environment variables are missing.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    # Read required configuration
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if not azure_endpoint:
        raise ValueError("Environment variable AZURE_OPENAI_ENDPOINT is required.")

    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-07-01-preview")
    deployment = deployment_name if deployment_name else model_name

    use_managed_identity = os.getenv("AZURE_USE_MANAGED_IDENTITY", "false").lower() == "true"

    if use_managed_identity:
        # Use Azure Identity via DefaultAzureCredential
        client_id = os.getenv("AZURE_MANAGED_IDENTITY_CLIENT_ID")
        # If a client id is provided, pass it to DefaultAzureCredential
        if client_id:
            credential = DefaultAzureCredential(managed_identity_client_id=client_id)
        else:
            credential = DefaultAzureCredential()

        token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")

        try:
            azure_client = openai.AsyncAzureOpenAI(
                api_version=api_version,
                azure_endpoint=azure_endpoint,
                azure_ad_token_provider=token_provider,
                azure_deployment=deployment
            )
        except Exception as e:
            logger.error("Error creating AzureOpenAI client with managed identity: %s", str(e))
            raise
    else:
        # Use API Key authentication
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY must be provided if not using managed identity.")
        try:
            azure_client = openai.AsyncAzureOpenAI(
                api_version=api_version,
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                azure_deployment=deployment
            )
        except Exception as e:
            logger.error("Error creating AzureOpenAI client with API key: %s", str(e))
            raise

    # Create a PydanticAI OpenAIModel instance using the OpenAIProvider
    try:
        provider = OpenAIProvider(openai_client=azure_client)
        openai_model = OpenAIModel(
            model_name=model_name,
            provider=provider
        )
    except Exception as e:
        logger.error("Error creating PydanticAI OpenAIModel: %s", str(e))
        raise

    logger.info("Azure OpenAI model created with endpoint %s and deployment %s", azure_endpoint, deployment)
    return openai_model
