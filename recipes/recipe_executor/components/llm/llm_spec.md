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
- Do not need to pass api keys directly to model classes (do need to provide to AzureProvider)
- Use PydanticAI's provider-specific model classes, passing only the model name
  - pydantic_ai.models.openai.OpenAIModel (used for Azure OpenAI)
  - pydantic_ai.models.anthropic.AnthropicModel
  - pydantic_ai.models.gemini.GeminiModel
- Create a PydanticAI Agent with the model and a structured output type
- Use the `run_sync` method of the Agent to make requests
- CRITICAL: make sure to return the result.data in the call_llm method

## Logging

- Debug: Log full request payload before making call and then full response payload after receiving it
- Info: Log model name and provider (no payload details) and response times

## Component Dependencies

The LLM component depends on:

- **Models** - Uses FileGenerationResult and FileSpec for structured output
- **Azure OpenAI** - Uses get_azure_openai_model for Azure OpenAI model initialization
- **External Libraries**: Relies on pydantic-ai for model, Agent, and LLM interactions

## Error Handling

- Provide clear error messages for unsupported providers
- Handle network and API errors gracefully
- Log detailed error information for debugging

## Future Considerations

- Additional LLM providers
- Enhanced parameter control for model fine-tuning
