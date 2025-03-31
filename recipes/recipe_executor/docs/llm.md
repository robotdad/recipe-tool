# LLM Component Usage

## Importing

```python
from recipe_executor.llm import get_model, get_agent, call_llm
```

## Basic Usage

The LLM component provides three main functions:

### 1. Getting a Model

```python
def get_model(model_id: str) -> Any:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider:model_name'.

    Args:
        model_id (str): Model identifier in format 'provider:model_name'.
                        Example: 'openai:o3-mini', 'anthropic:claude-3.7-sonnet-latest'.

    Returns:
        The model instance for the specified provider and model.

    Raises:
        ValueError: If model_id format is invalid or if the provider is unsupported.
    """
```

Usage example:

```python
# Get an OpenAI model
openai_model = get_model("openai:o3-mini")

# Get an Anthropic model
anthropic_model = get_model("anthropic:claude-3.7-sonnet-latest")

# Get a Gemini model
gemini_model = get_model("gemini:gemini-pro")
```

### 2. Creating an Agent

```python
def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize an LLM agent with the specified model.

    Args:
        model_id (Optional[str]): Model identifier in format 'provider:model_name'.
                                 If None, defaults to 'openai:gpt-4o'.

    Returns:
        Agent[None, FileGenerationResult]: A configured Agent ready to process LLM requests.
    """
```

Usage example:

```python
# Get default agent (openai:gpt-4o)
default_agent = get_agent()

# Get agent with specific model
custom_agent = get_agent(model_id="anthropic:claude-3-sonnet")
```

### 3. Calling an LLM

```python
def call_llm(prompt: str, model: Optional[str] = None) -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
        prompt (str): The prompt string to be sent to the LLM.
        model (Optional[str]): The model identifier in the format 'provider:model_name'.
        If None, defaults to 'openai:gpt-4o'.

    Returns:
        FileGenerationResult: The structured result containing generated files and commentary.

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
provider:model_name
```

Supported providers:

- `openai`: OpenAI models (e.g., `openai:gpt-4o`, `openai:o3-mini`)
- `anthropic`: Anthropic models (e.g., `anthropic:claude-3.7-sonnet-latest`)
- `gemini`: Google Gemini models (e.g., `gemini:gemini-pro`)

## System Prompt

The agent is configured with a system prompt that instructs the LLM to generate a JSON object with:

1. A `files` array containing file objects with `path` and `content` properties
2. An optional `commentary` field with additional information

This ensures consistent output structure regardless of the model used.

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
5. The agent is configured with 3 retries by default
