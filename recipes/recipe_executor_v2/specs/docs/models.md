# Models Component Usage

## Importing

```python
from recipe_executor.models import (
    FileSpec,
    FileGenerationResult,
    ReadFileConfig,
    GenerateCodeConfig,
    WriteFileConfig,
    RecipeStep,
    Recipe
)
```

## File Generation Models

### FileSpec

Represents a single file to be generated:

```python
class FileSpec(BaseModel):
    """Represents a single file to be generated.

    Attributes:
        path (str): Relative path where the file should be written.
        content (str): The content of the file.
    """

    path: str
    content: str
```

Usage example:

```python
file = FileSpec(
    path="src/utils.py",
    content="def hello_world():\n    print('Hello, world!')"
)

# Access properties
print(file.path)      # src/utils.py
print(file.content)   # def hello_world():...
```

### FileGenerationResult

Contains a collection of generated files and optional commentary:

```python
class FileGenerationResult(BaseModel):
    """Result of an LLM file generation request.

    Attributes:
        files (List[FileSpec]): List of files to generate.
        commentary (Optional[str]): Optional commentary from the LLM.
    """

    files: List[FileSpec]
    commentary: Optional[str] = None
```

Usage example:

```python
result = FileGenerationResult(
    files=[
        FileSpec(path="src/utils.py", content="def util_function():\n    pass"),
        FileSpec(path="src/main.py", content="from utils import util_function")
    ],
    commentary="Generated utility module and main script"
)

# Iterate through files
for file in result.files:
    print(f"Writing to {file.path}")
    # ... write file.content to file.path
```

## Step Configuration Models

### ReadFileConfig

Configuration for a ReadFile step:

```python
class ReadFileConfig(BaseModel):
    """Configuration for a ReadFile step.

    Attributes:
        file_path (str): The path of the file to read.
        store_key (str): Key under which to store the file content. Defaults to "spec".
    """

    file_path: str
    store_key: str = "spec"
```

Usage example:

```python
config = ReadFileConfig(
    file_path="specs/component_spec.md",
    store_key="component_spec"
)

# Use in a step definition
step = {
    "type": "read_file",
    "file_path": config.file_path,
    "store_key": config.store_key
}
```

### GenerateCodeConfig

Configuration for a GenerateCode step:

```python
class GenerateCodeConfig(BaseModel):
    """Configuration for a GenerateCode step.

    Attributes:
        input_key (str): Key in context where the specification is stored. Defaults to "spec".
        output_key (str): Key to store the generated code result. Defaults to "codegen_result".
    """

    input_key: str = "spec"
    output_key: str = "codegen_result"
```

### WriteFileConfig

Configuration for a WriteFile step:

```python
class WriteFileConfig(BaseModel):
    """Configuration for a WriteFile step.

    Attributes:
        input_key (str): Key in context where the codegen result is stored. Defaults to "codegen_result".
        output_root (str): Root directory where files will be written.
    """

    input_key: str = "codegen_result"
    output_root: str
```

## Recipe Models

### RecipeStep

Represents a single step in a recipe:

```python
class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type (str): The type of the recipe step.
        config (Dict): Dictionary containing configuration for the step.
    """

    type: str
    config: Dict
```

### Recipe

Represents a complete recipe with multiple steps:

```python
class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """

    steps: List[RecipeStep]
```

Usage example:

```python
from recipe_executor.models import Recipe, RecipeStep

# Create a recipe with steps
recipe = Recipe(
    steps=[
        RecipeStep(
            type="read_file",
            config={"file_path": "specs/component_spec.md", "store_key": "spec"}
        ),
        RecipeStep(
            type="generate",
            config={
                "prompt": "Generate code for: {{spec}}",
                "model": "openai:o3-mini",
                "artifact": "code_result"
            }
        ),
        RecipeStep(
            type="write_file",
            config={"artifact": "code_result", "root": "./output"}
        )
    ]
)

# Validate recipe structure
recipe_dict = recipe.dict()
```

## Model Validation

All models inherit from Pydantic's BaseModel, providing automatic validation:

```python
# This will raise a validation error because path is required
try:
    FileSpec(content="File content")
except Exception as e:
    print(f"Validation error: {e}")

# This works correctly
valid_file = FileSpec(path="file.txt", content="File content")
```

## Important Notes

1. Models provide runtime validation in addition to static type checking
2. Default values are provided for common configuration options
3. Models can be converted to dictionaries with `.dict()` method
4. Models can be created from dictionaries with `Model(**dict_data)`
