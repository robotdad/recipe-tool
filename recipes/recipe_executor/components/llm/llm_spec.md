# LLM Component Specification

## Purpose

The LLM component provides a unified interface for interacting with various large language model providers. It handles model initialization, request formatting, and response processing, enabling the Recipe Executor to generate content with different LLM providers through a consistent API.

## Core Requirements

- Support multiple LLM providers (Azure OpenAI, OpenAI, Anthropic, Gemini (not Vertex))
- Provide model initialization based on a standardized model identifier format
- Encapsulate LLM API details behind a unified interface
- Use PydanticAI for consistent handling and validation of LLM responses
- Implement basic error handling
- Support structured output format for file generation

## Implementation Considerations

- Use a clear provider:model_name identifier format
- Direct usage of provider SDKs through PydanticAI
- Load api keys and endpoints from environment variables, validating their presence
- Do not need to pass api keys directly to model classes (do need to provide to AzureProvider)
- Use PydanticAI's provider-specific model classes, passing the model name
  - pydantic_ai.models.openai.OpenAIModel (used for Azure OpenAI)
  - pydantic_ai.models.anthropic.AnthropicModel
  - pydantic_ai.models.gemini.GeminiModel
- Return agent.run_async(prompt).data as a FileGenerationResult object
- Minimal wrapper functions with clear responsibilities
- Consistent error handling with informative messages

### Implementation Hints

```python
def get_model(model_id: str) -> Union[OpenAIModel, AnthropicModel, GeminiModel]:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider:model_name' or 'provider:model_name:deployment_name'.

    Supported providers:
    - openai
    - anthropic
    - gemini
    - azure (for Azure OpenAI, use 'azure:model_name:deployment_name' or 'azure:model_name')

    Args:
        model_id (str): Model identifier in format 'provider:model_name'
            or 'provider:model_name:deployment_name'.
            If None, defaults to 'openai:gpt-4o'.

    Returns:
        The model instance for the specified provider and model.

    Raises:
        ValueError: If model_id format is invalid or if the provider is unsupported.
    """
```

Usage example:

```python
# Get an OpenAI model
openai_model = get_model("openai:o3-mini")
# Uses OpenAIModel('o3-mini')

# Get an Anthropic model
anthropic_model = get_model("anthropic:claude-3.7-sonnet-latest")
# Uses AnthropicModel('claude-3.7-sonnet-latest')

# Get a Gemini model
gemini_model = get_model("gemini:gemini-pro")
# Uses GeminiModel('gemini-pro')
```

```python
def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize an LLM agent with the specified model.

    Args:
        model_id (Optional[str]): Model identifier in format 'provider:model_name'.
        If None, defaults to 'openai:gpt-4o'.

    Returns:
        Agent[None, FileGenerationResult]: A configured Agent ready to process LLM requests.
    """
```

Usage example:

```python
# Get default agent (openai:gpt-4o)
default_agent = get_agent()

# Get agent with specific model
custom_agent = get_agent(model_id="anthropic:claude-3.7-sonnet-latest")
```

## Special Considerations for Azure OpenAI

- For Azure OpenAI, the format has two options:
  - `azure:model_name:deployment_name`
  - `azure:model_name` (uses model_name as deployment_name)
- Create OpenAIModel using pydantic_ai.providers.azure.AzureProvider
- Create custom client using AsyncAzureOpenAI from `openai` library
- Obtain AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_DEPLOYMENT_NAME from environment variables
- Optional AZURE_OPENAI_API_VERSION (defaults to 2025-03-01-preview)
- If AZURE_USE_MANAGED_IDENTITY is set, use the managed identity for authentication
  - If AZURE_MANAGED_IDENTITY_CLIENT_ID is set, use ManagedIdentityCredential
  - Otherwise, use DefaultAzureCredential
- If AZURE_USE_MANAGED_IDENTITY is not set, use the AZURE_OPENAI_API_KEY from environment variables

### AzureProvider Initialization Requirements

- CRITICAL: AzureProvider DOES NOT ACCEPT a deployment_name parameter
- CRITICAL: When using openai_client, do NOT provide azure_endpoint, api_version, or api_key
- For API key authentication, ONLY use this pattern:
  ```python
  # API key auth without custom client
  provider_instance = AzureProvider(
      azure_endpoint=AZURE_OPENAI_ENDPOINT,
      api_version=AZURE_OPENAI_API_VERSION,
      api_key=AZURE_OPENAI_API_KEY
  )
  ```
- For managed identity authentication, this EXACT implementation MUST be used:

  ```python
  # Create a token provider function with the REQUIRED scope
  # DO NOT directly use credential.get_token without a scope - it will fail
  # THIS IS THE MOST CRITICAL PART OF THE IMPLEMENTATION
  def get_bearer_token_provider():
      # This specific scope is required for Azure OpenAI
      scope = "https://cognitiveservices.azure.com/.default"
      # CRUCIAL: get_token returns an AccessToken object, but we need just the token string
      token = credential.get_token(scope)
      return token.token  # Extract just the string token from the AccessToken object

  # Pass the token provider FUNCTION, not the direct get_token method
  custom_client = AsyncAzureOpenAI(
      azure_endpoint=AZURE_OPENAI_ENDPOINT,
      api_version=AZURE_OPENAI_API_VERSION,
      azure_ad_token_provider=get_bearer_token_provider  # This is a function reference
  )

  # ONLY pass the custom client, NO other parameters
  provider_instance = AzureProvider(
      openai_client=custom_client
  )
  ```

- NEVER call credential.get_token directly without a scope
- NEVER pass deployment_name to AzureProvider
- The token scope "https://cognitiveservices.azure.com/.default" is REQUIRED
- Create a separate function for the token provider
- The OpenAI SDK handles deployment names through the model name parameter

## Logging

- Debug: Log all LLM calls with full request payload, response payload, and response times
- Info: Log all LLM calls with model name and provider (no payload details)

## Component Dependencies

The LLM component depends on:

- **Models** - Uses FileGenerationResult and FileSpec for structured output
- **External Libraries**:
  - Relies on pydantic-ai for model interactions and Azure Identity for authentication
  - The `openai` library is installed as a dependency for Azure OpenAI

## Error Handling

- Provide clear error messages for unsupported providers
- Handle network and API errors gracefully
- Log detailed error information for debugging

## Future Considerations

- Additional LLM providers
- Enhanced parameter control for model fine-tuning
