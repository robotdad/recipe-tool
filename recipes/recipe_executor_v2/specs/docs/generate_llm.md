# GenerateWithLLMStep Component Usage

## Importing

```python
from recipe_executor.steps.generate_llm import GenerateWithLLMStep, GenerateLLMConfig
```

## Configuration

The GenerateWithLLMStep is configured with a GenerateLLMConfig:

```python
class GenerateLLMConfig(StepConfig):
    """
    Config for GenerateWithLLMStep.

    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        model: The model identifier to use (provider:model_name format).
        artifact: The name under which to store the LLM response in context.
    """

    prompt: str
    model: str
    artifact: str
```

## Step Registration

The GenerateWithLLMStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.generate_llm import GenerateWithLLMStep

STEP_REGISTRY["generate"] = GenerateWithLLMStep
```

## Basic Usage in Recipes

The GenerateWithLLMStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "generate",
      "prompt": "Generate Python code for a utility that: {{requirements}}",
      "model": "openai:o3-mini",
      "artifact": "generation_result"
    }
  ]
}
```

## Template-Based Prompts

The prompt can include template variables from the context:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "specs/component_spec.md",
      "artifact": "spec"
    },
    {
      "type": "generate",
      "prompt": "You are an expert Python developer. Based on the following specification, generate code for a component:\n\n{{spec}}",
      "model": "openai:o3-mini",
      "artifact": "codegen_result"
    }
  ]
}
```

## Dynamic Model Selection

The model identifier can also use template variables:

```json
{
  "steps": [
    {
      "type": "generate",
      "prompt": "Generate code based on: {{spec}}",
      "model": "{{model_provider|default:'openai'}}:{{model_name|default:'o3-mini'}}",
      "artifact": "codegen_result"
    }
  ]
}
```

## Dynamic Artifact Keys

The artifact key can be templated to create dynamic storage locations:

```json
{
  "steps": [
    {
      "type": "generate",
      "prompt": "Generate code for: {{component_name}}",
      "model": "openai:o3-mini",
      "artifact": "{{component_name}}_result"
    }
  ]
}
```

## Implementation Details

The GenerateWithLLMStep works by:

1. Rendering the prompt with the current context
2. Rendering the model identifier
3. Rendering the artifact key (if it contains templates)
4. Calling the LLM with the rendered prompt and model
5. Storing the result in the context under the artifact key

```python
def execute(self, context: Context) -> None:
    # Process the artifact key using templating if needed
    artifact_key = self.config.artifact
    if "{{" in artifact_key and "}}" in artifact_key:
        artifact_key = render_template(artifact_key, context)

    # Render the prompt and model with the current context
    rendered_prompt = render_template(self.config.prompt, context)
    rendered_model = render_template(self.config.model, context)

    # Call the LLM
    self.logger.info(f"Calling LLM with prompt for artifact: {artifact_key}")
    response = call_llm(rendered_prompt, rendered_model)

    # Store the LLM response in context
    context[artifact_key] = response
    self.logger.debug(f"LLM response stored in context under '{artifact_key}'")
```

## LLM Response Format

The response from call_llm is a FileGenerationResult object:

```python
# FileGenerationResult structure
result = FileGenerationResult(
    files=[
        FileSpec(path="src/main.py", content="print('Hello, world!')"),
        FileSpec(path="src/utils.py", content="def add(a, b):\n    return a + b")
    ],
    commentary="Generated a simple Python project"
)
```

## Error Handling

The GenerateWithLLMStep can raise several types of errors:

```python
try:
    generate_step.execute(context)
except ValueError as e:
    # Template rendering or model format errors
    print(f"Value error: {e}")
except RuntimeError as e:
    # LLM call failures
    print(f"Runtime error: {e}")
```

## Common Use Cases

1. **Code Generation**:

   ```json
   {
     "type": "generate",
     "prompt": "Generate Python code for: {{specification}}",
     "model": "openai:o3-mini",
     "artifact": "code_result"
   }
   ```

2. **Content Creation**:

   ```json
   {
     "type": "generate",
     "prompt": "Write a blog post about: {{topic}}",
     "model": "anthropic:claude-3-haiku",
     "artifact": "blog_post"
   }
   ```

3. **Analysis and Transformation**:
   ```json
   {
     "type": "generate",
     "prompt": "Analyze this code and suggest improvements:\n\n{{code}}",
     "model": "openai:gpt-4o",
     "artifact": "code_analysis"
   }
   ```

## Important Notes

1. The artifact key can be dynamic using template variables
2. The prompt is rendered using the current context before sending to the LLM
3. The model identifier follows the format "provider:model_name"
4. The LLM response is a FileGenerationResult object with files and commentary
5. LLM calls may incur costs with the respective provider
