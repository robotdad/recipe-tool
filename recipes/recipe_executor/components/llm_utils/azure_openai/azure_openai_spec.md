# Azure OpenAI Component Specification

## Purpose

The Azure OpenAI component provides a PydanticAI wrapper for Azure OpenAI models for use with PydanticAI Agents. It handles model initialization and authentication.

## Core Requirements

- Provide a PydanticAI-compatible OpenAIModel instance
- Support choice of api key or Azure Identity for authentication
- Use the `openai` library for Azure OpenAI client
- Implement basic error handling

## Implementation Considerations

- Load api keys and endpoints from environment variables, validating their presence
- If using Azure Identity:
  - AsyncAzureOpenAI client must be created with a token provider function
  - If using a custom client ID, use `ManagedIdentityCredential` with the specified client ID
- Create an `openai.AzureOpenAI` client with the provided token provider or API key
- Create a `pydantic_ai.providers.openai.OpenAIProvider` with the Azure OpenAI client
- Return a `pydantic_ai.models.openai.OpenAIModel` with the model name and provider

## Implementation Hints

```python
azure_client = AsyncAzureOpenAI(
    azure_ad_token_provider=token_provider,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
)

openai_model = OpenAIModel(
    model_name,
    provider=OpenAIProvider(openai_client=azure_client),
)
```

## Component Dependencies

The Azure OpenAI component depends on:

- **External Libraries**:
  - Relies on PydanticAI for model interactions and Azure Identity for authentication
  - The `pydantic-ai`, `openai`, and `azure-identity` libraries are installed as dependencies

## Error Handling

- Log detailed error information for debugging
