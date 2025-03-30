# GenerateWithLLMStep Component Specification

## Purpose

The GenerateWithLLMStep component enables recipes to generate content using large language models (LLMs). It serves as the bridge between recipes and the LLM subsystem, handling prompt templating, model selection, and storing generation results in the context.

## Core Requirements

1. Process prompt templates using context data
2. Support configurable model selection
3. Call LLMs to generate content
4. Store generated results in the context
5. Support dynamic artifact key resolution
6. Include appropriate logging for LLM operations

## Implementation Considerations

- Use template rendering for dynamic prompt generation
- Support template rendering in model selection
- Allow dynamic artifact key through template rendering
- Keep the implementation simple and focused on a single responsibility
- Log detailed information about LLM requests

## Component Dependencies

The GenerateWithLLMStep component depends on:

1. **Steps Base** - Extends BaseStep with a specific config type
2. **Context** - Retrieves input values and stores generation results
3. **LLM** - Uses call_llm function to interact with language models
4. **Utils** - Uses render_template for dynamic content resolution

## Error Handling

- Handle LLM-related errors gracefully
- Log LLM call failures with meaningful context
- Ensure proper error propagation for debugging
- Validate configuration before making LLM calls

## Future Considerations

1. Support for streaming LLM responses
2. Additional LLM parameters (temperature, max tokens, etc.)
3. Prompt library integration
4. Caching of common generations
