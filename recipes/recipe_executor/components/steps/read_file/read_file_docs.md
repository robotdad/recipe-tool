# ReadFileStep Component Usage

## Importing

```python
from recipe_executor.steps.read_file import ReadFileStep, ReadFileConfig
```

## Configuration

The ReadFileStep is configured with a ReadFileConfig:

```python
class ReadFileConfig(StepConfig):
    """
    Configuration for ReadFileStep.

    Fields:
        path (str): Path to the file to read (may be templated).
        artifact (str): Name to store the file contents in context.
        optional (bool): Whether to continue if the file is not found.
    """

    path: str
    artifact: str
    optional: bool = False
```

## Step Registration

The ReadFileStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.read_file import ReadFileStep

STEP_REGISTRY["read_file"] = ReadFileStep
```

## Basic Usage in Recipes

The ReadFileStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "specs/component_spec.md",
      "artifact": "component_spec"
    }
  ]
}
```

## Template-Based Paths

The path can include template variables from the context:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "specs/{{component_id}}_spec.md",
      "artifact": "component_spec"
    }
  ]
}
```

## Optional Files

You can specify that a file is optional, and execution will continue even if the file doesn't exist:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "specs/optional_file.md",
      "artifact": "optional_content",
      "optional": true
    }
  ]
}
```

If an optional file is not found, an empty string is stored in the context.

## Implementation Details

The ReadFileStep works by:

1. Resolving the path using template rendering
2. Checking if the file exists
3. Reading the file content
4. Storing the content in the context

```python
def execute(self, context: Context) -> None:
    # Render the path using the current context
    path = render_template(self.config.path, context)

    # Check if file exists
    if not os.path.exists(path):
        if self.config.optional:
            self.logger.warning(f"Optional file not found at path: {path}, continuing anyway")
            context[self.config.artifact] = ""  # Set empty string for missing optional file
            return
        else:
            raise FileNotFoundError(f"ReadFileStep: file not found at path: {path}")

    # Read the file
    self.logger.info(f"Reading file from: {path}")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Store in context
    context[self.config.artifact] = content
    self.logger.debug(f"Stored file contents in context under key: '{self.config.artifact}'")
```

## Error Handling

If a file doesn't exist and is not marked as optional, the step will raise a FileNotFoundError:

```python
try:
    read_file_step.execute(context)
except FileNotFoundError as e:
    print(f"File error: {e}")
    # Handle the error
```

## Common Use Cases

1. **Loading Specifications**:

   ```json
   {
     "type": "read_file",
     "path": "specs/component_spec.md",
     "artifact": "spec"
   }
   ```

2. **Loading Templates**:

   ```json
   {
     "type": "read_file",
     "path": "templates/email_template.txt",
     "artifact": "email_template"
   }
   ```

3. **Dynamic Path Resolution**:
   ```json
   {
     "type": "read_file",
     "path": "docs/{{project}}/{{component}}.md",
     "artifact": "documentation"
   }
   ```

## Important Notes

1. The step uses UTF-8 encoding by default
2. The file content is stored as a string in the context
3. Template variables in the path are resolved before reading the file
4. When a file is optional and missing, an empty string is stored
