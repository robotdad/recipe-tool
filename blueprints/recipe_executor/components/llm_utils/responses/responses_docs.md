# Responses Component Documentation

The Responses component provides OpenAI built-in tool integration for Recipe Executor.

## Overview

This component handles OpenAI's Responses API built-in tools (web search, code execution) 
by creating configured `OpenAIResponsesModel` instances with appropriate tool settings.

## Usage

### Basic Usage (Phase 1)

```python
from recipe_executor.llm_utils.responses import create_openai_responses_model

# Create basic responses model
model = create_openai_responses_model("gpt-4o")

# Use with PydanticAI Agent
from pydantic_ai import Agent
agent = Agent(model=model)
result = await agent.run("Hello, what can you do with the Responses API?")
```

### Phase 3 Features (Future)

Built-in tools support (web search, code execution) will be added in Phase 3 via the `llm_generate` step, not in this component.

## Integration with LLM Component

The LLM component routes `openai_responses/*` model identifiers to this component:

```python
# In llm.py get_model() function:
if provider == "openai_responses":
    from recipe_executor.llm_utils.responses import create_openai_responses_model
    model_name = parts[1]
    model = create_openai_responses_model(model_name)
    return model
```

## Phase 1 Scope

Currently provides basic OpenAI Responses API model creation. Built-in tools (web search, code execution) will be added in Phase 3.

## Error Handling

- **Model initialization errors**: Clear error messages for OpenAI model creation failures
- **Invalid model names**: Validation errors with helpful context