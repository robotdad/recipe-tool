# WriteFileStep Component Usage

## Importing

```python
from recipe_executor.steps.write_files import WriteFileStep, WriteFilesConfig
```

## Configuration

The WriteFileStep is configured with a WriteFilesConfig:

```python
class WriteFilesConfig(StepConfig):
    """
    Config for WriteFileStep.

    Fields:
        artifact: Name of the context key holding a FileGenerationResult or List[FileSpec].
        root: Optional base path to prepend to all output file paths.
    """

    artifact: str
    root: str = "."
```

## Step Registration

The WriteFileStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.write_files import WriteFileStep

STEP_REGISTRY["write_file"] = WriteFileStep
```

## Basic Usage in Recipes

The WriteFileStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "write_file",
      "artifact": "generated_code",
      "root": "output/project"
    }
  ]
}
```

## Supported Context Values

The WriteFileStep can work with two types of artifacts in the context:

### 1. FileGenerationResult

```python
from recipe_executor.models import FileGenerationResult, FileSpec

# Example of generating a FileGenerationResult
result = FileGenerationResult(
    files=[
        FileSpec(path="src/main.py", content="print('Hello, world!')"),
        FileSpec(path="src/utils.py", content="def add(a, b):\n    return a + b")
    ],
    commentary="Generated a simple Python project"
)

# Store in context
context["generated_code"] = result
```

### 2. List of FileSpec objects

```python
from recipe_executor.models import FileSpec

# Example of generating a list of FileSpec objects
files = [
    FileSpec(path="src/main.py", content="print('Hello, world!')"),
    FileSpec(path="src/utils.py", content="def add(a, b):\n    return a + b")
]

# Store in context
context["generated_files"] = files
```

## Using Template Variables

The root path and individual file paths can include template variables:

```json
{
  "steps": [
    {
      "type": "write_file",
      "artifact": "generated_code",
      "root": "output/{{project_name}}"
    }
  ]
}
```

File paths within the FileSpec objects can also contain templates:

```python
FileSpec(
    path="{{component_name}}/{{filename}}.py",
    content="# Generated code for {{component_name}}"
)
```

## Implementation Details

The WriteFileStep works by:

1. Retrieving the artifact from the context
2. Validating it's a FileGenerationResult or list of FileSpec objects
3. Rendering the root path using template rendering
4. For each file:
   - Rendering the file path
   - Creating the necessary directories
   - Writing the file content

```python
def execute(self, context: Context) -> None:
    # Get data from context
    data = context.get(self.config.artifact)

    if data is None:
        raise ValueError(f"No artifact found at key: {self.config.artifact}")

    # Determine file list
    if isinstance(data, FileGenerationResult):
        files = data.files
    elif isinstance(data, list) and all(isinstance(f, FileSpec) for f in data):
        files = data
    else:
        raise TypeError("Expected FileGenerationResult or list of FileSpec objects")

    # Render output root
    output_root = render_template(self.config.root, context)

    # Write each file
    for file in files:
        rel_path = render_template(file.path, context)
        full_path = os.path.join(output_root, rel_path)

        # Create directories
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Write file
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(file.content)

        self.logger.info(f"Wrote file: {full_path}")
```

## Error Handling

The WriteFileStep can raise several types of errors:

```python
try:
    write_step.execute(context)
except ValueError as e:
    # Missing or invalid artifact
    print(f"Value error: {e}")
except TypeError as e:
    # Unexpected artifact type
    print(f"Type error: {e}")
except IOError as e:
    # File writing errors
    print(f"I/O error: {e}")
```

## Common Use Cases

1. **Writing Generated Code**:

   ```json
   {
     "type": "write_file",
     "artifact": "generated_code",
     "root": "output/src"
   }
   ```

2. **Project-Specific Output**:

   ```json
   {
     "type": "write_file",
     "artifact": "project_files",
     "root": "output/{{project_name}}"
   }
   ```

3. **Component Generation**:
   ```json
   {
     "type": "write_file",
     "artifact": "component_result",
     "root": "output/components"
   }
   ```

## Important Notes

1. Directories are created automatically if they don't exist
2. Files are overwritten without confirmation if they already exist
3. All paths are rendered using template variables from the context
4. File content is written using UTF-8 encoding
5. Both FileGenerationResult and List[FileSpec] formats are supported
