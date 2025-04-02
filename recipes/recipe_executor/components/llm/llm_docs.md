# LLM Component Usage

## Importing

```python
from recipe_executor.llm import call_llm
```

## Basic Usage

The LLM component provides one main function:

```python
def call_llm(prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = "RecipeExecutor") -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
        prompt (str): The prompt string to be sent to the LLM.
        model (Optional[str]): The model identifier in the format 'provider:model_name' (or 'provider:model_name:deployment_name').
        If None, defaults to 'openai:gpt-4o'.
        logger (Optional[logging.Logger]): Logger instance, defaults to "RecipeExecutor"

    Returns:
        FileGenerationResult: The structured result data containing generated files and commentary.

    Raises:
        Exception: If model value cannot be mapped to valid provider/model_name , LLM call fails, or result validation fails.
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

### Supported providers:

#### Azure OpenAI

```python
# Example model IDs
model=`azure:gpt-4o:deployment_name`
model=`azure:o3-mini` # if deployment_name is the same as model_name
```

Authentication environment variables (.e.g., in .env file):

```bash
# Option 1: Managed identity with default managed identity
AZURE_USE_MANAGED_IDENTITY=true # Set to true to use managed identity
AZURE_OPENAI_ENDPOINT= # Required
AZURE_OPENAI_API_VERSION= # Optional, defaults to 2025-03-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME= # Optional, defaults to model_name
```

```bash
# Option 2: Managed identity with custom client ID
AZURE_USE_MANAGED_IDENTITY=true # Set to true to use managed identity
AZURE_MANAGED_IDENTITY_CLIENT_ID= # Required
AZURE_OPENAI_ENDPOINT= # Required
AZURE_OPENAI_API_VERSION= # Optional, defaults to 2025-03-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME= # Optional, defaults to model_name
```

```bash
# Option 3: API key authentication
AZURE_OPENAI_API_KEY= # Required
AZURE_OPENAI_ENDPOINT= # Required
AZURE_OPENAI_API_VERSION= # Optional, defaults to 2025-03-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME= # Optional, defaults to model_name
```

````

#### OpenAI

```python
# Example model IDs
model=`openai:gpt-4o`
model=`openai:o3-mini`
````

Authentication environment variables (.e.g., in .env file):

```bash
OPENAI_API_KEY= # Required
```

#### Anthropic

```python
# Example model IDs
model=`anthropic:claude-3.7-sonnet-latest`
```

Authentication environment variables (.e.g., in .env file):

```bash
ANTHROPIC_API_KEY= # Required
```

#### Gemini

```python
# Example model IDs
model=`gemini:gemini-2.5`
```

Authentication environment variables (.e.g., in .env file):

```bash
GEMINI_API_KEY= # Required
```

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

- Calling a model incurs API costs with the respective provider
- OpenAI is the default provider if none is specified
- The component logs request details at debug level
- Responses are validated against the FileGenerationResult model
