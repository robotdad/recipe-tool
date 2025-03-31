# LLM Component Specification

## Purpose

The LLM component provides a unified interface for interacting with various large language model providers. It handles model initialization, request formatting, and response processing, enabling the Recipe Executor to generate content with different LLM providers through a consistent API.

## Core Requirements

- Support multiple LLM providers (OpenAI, Anthropic, Gemini, Azure OpenAI)
- Provide model initialization based on a standardized model identifier format
- Encapsulate LLM API details behind a unified interface
- Use Pydantic AI for consistent handling and validation of LLM responses
- Implement basic error handling and retry logic
- Support structured output format for file generation
- Support Azure OpenAI with both API key and managed identity authentication
- Handle Azure-specific configuration requirements (endpoint, deployment name)

## Implementation Considerations

- Use a clear provider:model_name identifier format
- Direct usage of provider SDKs through pydantic-ai
- Minimal wrapper functions with clear responsibilities
- Consistent error handling with informative messages
- Logging of request details and timing information
- Use azure:model_name:deployment_name format for Azure OpenAI models
- Support authentication through both API key and Azure managed identity
- Leverage azure-identity library for managed identity token acquisition

## Azure OpenAI Integration

- DO NOT create or import a separate AzureOpenAIModel class - it does not exist in pydantic-ai
- Use the existing OpenAIModel class with the AzureProvider for Azure OpenAI integration
- Import azure.identity for managed identity support (DefaultAzureCredential and ManagedIdentityCredential)
- Use AzureOpenAISettings from models.py to centralize configuration and environment variables

### Authentication Implementation Details
- Support both authentication methods with proper implementation:
  - API key authentication: Pass api_key directly to AzureProvider constructor
  - Managed identity authentication: 
    - Check for AZURE_USE_MANAGED_IDENTITY environment variable
    - Create a credential object (DefaultAzureCredential or ManagedIdentityCredential)
    - Create a custom AsyncAzureOpenAI client with azure_ad_token_provider=credential.get_token
    - Pass this custom client to AzureProvider via the openai_client parameter
    - IMPORTANT: Do NOT pass the credential object directly to AzureProvider
- Do not require API key when managed identity is enabled
- Use the appropriate credential based on the managed_identity_client_id setting
- Import openai.AsyncAzureOpenAI directly for creating the custom client
- Handle token acquisition errors properly for managed identity scenarios
- Provide clear error messages distinguishing between configuration issues

### Model and Deployment Name Handling
- Support two formats for Azure model IDs:
  - "azure:model_name" - Use model_name as both the model and deployment name
  - "azure:model_name:deployment_name" - Use explicit deployment_name
- Default behavior for get_agent() should follow the pattern used for OpenAI:
  - If no model_id is provided, default to "azure:gpt-4o" (similar to OpenAI's default)
  - This means default model AND deployment name should be "gpt-4o"
- Allow overriding via model_id parameter, not environment variables
- This maintains consistency with how OpenAI models are currently handled

### AzureProvider Initialization Requirements
- CRITICAL: AzureProvider DOES NOT ACCEPT a deployment_name parameter
- CRITICAL: When using openai_client, do NOT provide azure_endpoint, api_version, or api_key
- For API key authentication, ONLY use this pattern:
  ```python
  # API key auth without custom client
  provider_instance = AzureProvider(
      azure_endpoint=azure_endpoint,
      api_version=api_version,
      api_key=api_key
  )
  ```

### MANDATORY TOKEN SCOPE FOR MANAGED IDENTITY

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
      azure_endpoint=azure_endpoint,
      api_version=api_version,
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

## Component Dependencies

The LLM component depends on:

- **Models** - Uses FileGenerationResult and FileSpec for structured output
- **External Libraries** - Relies on pydantic-ai for model interactions

## Error Handling

- Provide clear error messages for unsupported providers
- Handle network and API errors gracefully
- Log detailed error information for debugging
- Include timing information for performance monitoring
- Add specific error handling for Azure authentication failures, especially for managed identity scenarios

## Future Considerations

- Additional LLM providers
- Enhanced parameter control for model fine-tuning
