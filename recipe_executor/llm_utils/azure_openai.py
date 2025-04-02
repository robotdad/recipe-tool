import logging
import os
from typing import Optional

import openai

# Import the PydanticAI model and provider for OpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# For managed identity, attempt to import the Azure Identity packages
try:
    from azure.identity import DefaultAzureCredential, ManagedIdentityCredential, get_bearer_token_provider
except ImportError as e:
    raise ImportError("azure-identity package is required for managed identity authentication.") from e


def get_openai_model(
    model_name: str, deployment_name: Optional[str] = None, logger: Optional[logging.Logger] = None
) -> OpenAIModel:
    """
    Create and return a PydanticAI OpenAIModel instance configured for Azure OpenAI Service.

    The function reads configuration values from environment variables and supports both API key and managed identity authentication.

    Environment Variables:
      - AZURE_OPENAI_ENDPOINT: The endpoint of your Azure OpenAI resource (required).
      - AZURE_OPENAI_API_VERSION: The API version to use (optional, defaults to "2023-07-01-preview").
      - AZURE_OPENAI_DEPLOYMENT: The deployment name (optional, defaults to the model name).
      - AZURE_USE_MANAGED_IDENTITY: If set to "true" or "1", managed identity is used instead of API key.
      - AZURE_MANAGED_IDENTITY_CLIENT_ID: (Optional) The client ID for a user-assigned managed identity.
      - AZURE_OPENAI_API_KEY: The API key to use when managed identity is not employed.

    Args:
      model_name: The name of the underlying model (e.g., "gpt-4o").
      deployment_name: Optional override for the deployment name; if not provided, falls back to AZURE_OPENAI_DEPLOYMENT or model_name.
      logger: Optional logger; if not provided, a logger named "RecipeExecutor" is used.

    Returns:
      An instance of OpenAIModel configured with the proper authentication and endpoint settings.

    Raises:
      ValueError: If required environment variables are missing.
      Exception: If there is an error initializing the client or model.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    # Read required Azure configuration values
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if not azure_endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT is not set in the environment.")

    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-07-01-preview")
    azure_deployment = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT", model_name)

    # Determine if managed identity should be used
    use_managed_identity = os.getenv("AZURE_USE_MANAGED_IDENTITY", "false").lower() in ("true", "1")

    if use_managed_identity:
        logger.info("Using managed identity authentication for Azure OpenAI.")
        client_id = os.getenv("AZURE_MANAGED_IDENTITY_CLIENT_ID")
        try:
            if client_id:
                credential = ManagedIdentityCredential(client_id=client_id)
            else:
                credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
        except Exception as e:
            logger.error("Error initializing token provider with managed identity: %s", e)
            raise e
        try:
            azure_client = openai.AsyncAzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                azure_deployment=azure_deployment,
                azure_ad_token_provider=token_provider,
            )
        except Exception as e:
            logger.error("Error initializing Azure OpenAI client with managed identity: %s", e)
            raise e
    else:
        logger.info("Using API key authentication for Azure OpenAI.")
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not azure_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY must be set when not using managed identity.")
        try:
            azure_client = openai.AsyncAzureOpenAI(
                api_key=azure_api_key,
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                azure_deployment=azure_deployment,
            )
        except Exception as e:
            logger.error("Error initializing Azure OpenAI client with API key: %s", e)
            raise e

    try:
        provider = OpenAIProvider(openai_client=azure_client)
        model = OpenAIModel(model_name, provider=provider)
    except Exception as e:
        logger.error("Error creating OpenAIModel: %s", e)
        raise e

    logger.info("Successfully created Azure OpenAI model for model '%s' with deployment '%s'.", model_name, azure_deployment)
    return model


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        model = get_openai_model("gpt-4o")
        print("Model created successfully:", model)
    except Exception as err:
        print("Failed to create model:", err)
