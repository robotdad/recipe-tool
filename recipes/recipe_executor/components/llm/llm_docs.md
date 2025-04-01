# LLM Component Usage

## Importing

```python
from recipe_executor.llm import call_llm
```

## Basic Usage

The LLM component provides one main function:

```python
def call_llm(prompt: str, model: Optional[str] = None) -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
        prompt (str): The prompt string to be sent to the LLM.
        model (Optional[str]): The model identifier in the format 'provider:model_name' (or 'provider:model_name:deployment_name').
        If None, defaults to 'openai:gpt-4o'.

    Returns:
        FileGenerationResult: The structured result data containing generated files and commentary.

    Raises:
        Exception: If LLM call fails or result validation fails.
    """
```

Usage example:

```python
# Call LLM with default model
result = call_llm("Generate a Python utility module for handling dates.")

# Call with specific model
result = call_llm(
    prompt="Create a React component for a user profile page.",
    model="openai:o3-mini"
)

# Access generated files
for file in result.files:
    print(f"File: {file.path}")
    print(file.content)

# Access commentary
if result.commentary:
    print(f"Commentary: {result.commentary}")
```

## Model ID Format

The component uses a standardized model identifier format:

```
All models:
provider:model_name

Additional option for Azure OpenAI (otherwise assume deployment_name is the same as model_name):
azure:model_name:deployment_name
```

Supported providers:

- `azure`: Azure OpenAI models (e.g., `azure:gpt-4o:deployment_name` or `azure:gpt-4o`)
- `openai`: OpenAI models (e.g., `openai:gpt-4o`, `openai:o3-mini`)
- `anthropic`: Anthropic models (e.g., `anthropic:claude-3.7-sonnet-latest`)
- `gemini`: Google Gemini models (e.g., `gemini:gemini-pro`)

## Error Handling

Example of error handling:

```python
try:
    result = call_llm(prompt, model_id)
    # Process result
except ValueError as e:
    # Handle invalid model ID or format
    print(f"Invalid model configuration: {e}")
except Exception as e:
    # Handle other errors (network, API, etc.)
    print(f"LLM call failed: {e}")
```

## Integration with Steps

The LLM component is primarily used by the GenerateWithLLMStep:

```python
# Example from GenerateWithLLMStep.execute()
def execute(self, context: Context) -> None:
    rendered_prompt = render_template(self.config.prompt, context)
    rendered_model = render_template(self.config.model, context)

    response = call_llm(rendered_prompt, rendered_model)

    artifact_key = render_template(self.config.artifact, context)
    context[artifact_key] = response
```

## Important Notes

1. Calling a model incurs API costs with the respective provider
2. OpenAI is the default provider if none is specified
3. The component logs request details at debug level
4. Responses are validated against the FileGenerationResult model
5. The llm calls will retry 3 times for transient errors
