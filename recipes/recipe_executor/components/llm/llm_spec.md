# LLM Component Specification

## Purpose

The LLM component provides a unified interface for interacting with various large language model providers. It handles model initialization, request formatting, and response processing, enabling the Recipe Executor to generate content with different LLM providers through a consistent API.

## Core Requirements

- Support multiple LLM providers (Azure OpenAI, OpenAI, Anthropic, Gemini)
- Provide model initialization based on a standardized model identifier format
- Encapsulate LLM API details behind a unified interface
- Use Pydantic AI for consistent handling and validation of LLM responses
- Implement basic error handling and retry logic
- Support structured output format for file generation

## Implementation Considerations

- Use a clear provider:model_name identifier format
- For Azure OpenAI, the format has two options:
  - `azure:model_name:deployment_name`
  - `azure:model_name` (uses model_name as deployment_name)
- Direct usage of provider SDKs through pydantic-ai
- Minimal wrapper functions with clear responsibilities
- Consistent error handling with informative messages

## Logging

- Debug: log all LLM calls with full request payload, response payload, and response times
- Info: log successful calls with model name and response summary

## Component Dependencies

The LLM component depends on:

- **Models** - Uses FileGenerationResult and FileSpec for structured output
- **External Libraries** - Relies on pydantic-ai for model interactions

## Error Handling

- Provide clear error messages for unsupported providers
- Handle network and API errors gracefully
- Log detailed error information for debugging

## Future Considerations

- Additional LLM providers
- Enhanced parameter control for model fine-tuning
