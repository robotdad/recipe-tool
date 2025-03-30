# LLM Component Specification for Recipe Executor

This document outlines the specifications for the LLM (Large Language Model) component of the Recipe Executor system. This component is responsible for interfacing with various LLM providers to generate code and other content based on specifications.

## Core Requirements

The LLM component should:

1. Integrate the Pydantic AI library for LLM interactions
2. Support multiple model providers (currently OpenAI, Anthropic, and Gemini)
3. Provide a consistent interface for making LLM requests regardless of the underlying provider
4. Return structured responses in a predictable format
5. Handle errors gracefully and provide meaningful feedback
6. Be configurable with different model settings

## Component Structure

The LLM component should consist of the following elements:

### 1. Model Provider Interface

```python
def get_model(model_id: str) -> Model:
    """
    Initialize an LLM model based on a standardized model_id string.
    Format: 'provider:model_name' (e.g., 'openai:gpt-4o', 'openai:o3-mini', 'anthropic:claude-3.7-sonnet-latest')

    Supported providers:
    - 'openai': OpenAI models using the OpenAI Python SDK
    - 'anthropic': Anthropic Claude models using the Anthropic Python SDK
    - 'gemini': Google Gemini models using the Google Generative AI Python SDK

    Returns a configured model instance ready for use.
    """
```

### 2. Agent Configuration

```python
def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize an LLM agent with the specified model.

    The agent should be configured with:
    - A default model if none specified (e.g., 'openai:gpt-4o')
    - A system prompt instructing it to generate file content
    - Retry logic (at least 3 retries)
    - Return type validation using FileGenerationResult

    Returns a configured agent ready to handle requests.
    """
```

### 3. LLM Request Function

```python
def call_llm(prompt: str, model: Optional[str] = None) -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured result.

    The function should:
    - Log the request prompt and timing information
    - Initialize the appropriate agent with the model
    - Handle errors gracefully
    - Return a FileGenerationResult containing generated files and commentary
    """
```

## Data Structures

The component should import and utilize the following data structures from the `recipe_executor` module, as needed:

```python
from recipe_executor.models import FileGenerationResult, FileSpec
```

### File Generation Result Structure Reference

```python
class FileSpec(BaseModel):
    """Represents a single file to be generated"""
    path: str  # Relative path where the file should be written
    content: str  # The content of the file

class FileGenerationResult(BaseModel):
    """Result of an LLM file generation request"""
    files: List[FileSpec]  # List of files to generate
    commentary: Optional[str] = None  # Optional commentary from the LLM
```

## Implementation Philosophy

Following the Cortex Platform implementation philosophy:

1. **Ruthless Simplicity**

   - Keep the interface minimal but complete
   - Avoid unnecessary abstractions
   - Start with essential functionality only

2. **Library Usage**

   - Use LLM libraries as intended with minimal wrappers
   - Direct integration with provider SDKs
   - Clear error handling

3. **Error Handling**
   - Provide useful error messages
   - Log detailed information for debugging
   - Implement reasonable retry logic

## Integration Points

The LLM component should integrate with:

1. **Context** - For accessing configuration and storing results
2. **Steps** - Particularly the GenerateWithLLMStep which will use this component
3. **Models** - For defining the structure of inputs and outputs

## Usage Example

The component should support usage patterns like:

```python
# Example of how the LLM component would be used in a generation step
prompt = render_template(self.config.prompt, context)
model_id = render_template(self.config.model, context)
result = call_llm(prompt, model_id)
context[artifact_key] = result  # Store the result in context
```

## System Prompt Requirements

The system prompt used should instruct the LLM to:

1. Generate JSON output with exactly two keys: 'files' and 'commentary'
2. Generate proper file content with correct escaping for special characters
3. Not to include any extraneous information outside the JSON structure

## Logging Requirements

The component should log to the root logger: "RecipeExecutor"

- LLM request prompts (debug level)
- Response timing information (debug level)
- Complete responses (debug level)
- Errors with detailed information (error level)

## Future Considerations

1. Support for additional LLM providers
2. Caching mechanisms for optimization
3. Enhanced parameter control for fine-tuning outputs
4. Integration with streaming responses
