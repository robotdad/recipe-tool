# Models Component Specification

## Purpose

The Models component defines the core data structures used throughout the Recipe Executor system. It provides Pydantic models for validating and structuring data, including recipe steps, file generation results, step configurations, and provider settings.

## Core Requirements

- Define consistent data structures for file generation results
- Provide configuration models for various step types
- Support recipe structure validation
- Leverage Pydantic for schema validation and documentation
- Include clear type hints and docstrings
- Support Azure OpenAI configuration with both API key and managed identity authentication options
- Provide validation for provider-specific settings

## Implementation Considerations

- Use Pydantic models for all data structures
- Keep models focused and minimal
- Provide sensible defaults where appropriate
- Use descriptive field names and docstrings
- Focus on essential fields without over-engineering
- Create AzureOpenAISettings class for Azure-specific configuration
- Use pydantic_settings.BaseSettings for environment variable handling
- Implement validation to ensure the proper authentication method is configured

## Azure OpenAI Settings

The AzureOpenAISettings class must:

- Implement a Pydantic model derived from BaseSettings
- Include the following fields:
  - endpoint: Required string for the Azure OpenAI service endpoint (from AZURE_OPENAI_ENDPOINT)
  - openai_api_version: Required string for the API version to use (from OPENAI_API_VERSION)
  - api_key: Optional string for API key authentication (from AZURE_OPENAI_API_KEY)
  - use_managed_identity: Boolean flag to enable managed identity, defaults to False (from AZURE_USE_MANAGED_IDENTITY)
  - managed_identity_client_id: Optional string for specific managed identity client ID (from AZURE_MANAGED_IDENTITY_CLIENT_ID)

- Implement validation that ensures:
  - API key is provided when managed identity is not used
  - Proper error messages for missing required fields
  
- Support reading from:
  - Environment variables with appropriate naming
  - Optional .env file configuration using pydantic-settings
  
- Authentication requirements:
  - Standard OpenAI API key (OPENAI_API_KEY) must NOT be required when using Azure OpenAI
  - Azure API key (AZURE_OPENAI_API_KEY) must NOT be required when managed identity is enabled
  - Either Azure API key OR managed identity must be configured
  - Provide clear validation error messages for authentication configuration issues
  - Ensure the validation logic correctly distinguishes between managed identity and API key auth

## Component Dependencies

The Models component has no external dependencies on other Recipe Executor components.

## Future Considerations

- Extended validation for complex fields
- Support for additional provider-specific settings
- Dynamic configuration based on environment variables
