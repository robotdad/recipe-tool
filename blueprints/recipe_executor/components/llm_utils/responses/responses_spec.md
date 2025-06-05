# Responses Component Specification

## Purpose

The Responses component provides OpenAI built-in tool integration using the PydanticAI Responses API.
It enables recipes to request OpenAI's built-in capabilities (web search, code execution)
via the `openai_responses` provider.

## Provider Identifiers

- `openai_responses` (OpenAI only - Azure handled by separate component)

## Core Requirements

- `create_openai_responses_model(model_name: str) -> OpenAIResponsesModel`

## Component Dependencies

- **LLM**: Invoked by `LLMGenerateStep` when model provider is `openai_responses`
- **PydanticAI**: Uses `OpenAIResponsesModel` for basic OpenAI Responses API access

## Implementation Considerations

- Generate a function `create_openai_responses_model` that:
  - Takes `model_name` (e.g., "gpt-4o") only
  - For OpenAI responses, instantiate `OpenAIResponsesModel(model_name)` 
  - Return the `OpenAIResponsesModel` instance directly
  - Built-in tools functionality will be added in Phase 3 via `llm_generate` step

## External Libraries

- **pydantic-ai**: Uses PydanticAI's `OpenAIResponsesModel`

## Error Handling

- Handle model initialization errors gracefully with clear error messages

## Output Files

- `recipe_executor/llm_utils/responses.py`