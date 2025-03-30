# Models Component Specification

## Purpose

The Models component defines the core data structures and Pydantic models used throughout the Recipe Executor system. These models provide type validation, documentation, and structured data handling for recipes, steps, and the output of LLM generation.

## Core Requirements

The Models component should:

1. Define Pydantic models for all key data structures
2. Provide clean validation for input/output data
3. Include clear documentation via docstrings and type hints
4. Support serialization to/from JSON
5. Follow a minimal design approach with only essential fields
6. Maintain separation of concerns between different model types

## Component Structure

The Models component should consist of the following key models:

### File-Related Models

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

### Configuration Models

```python
class ReadFileConfig(BaseModel):
    """Configuration for ReadFileStep"""
    file_path: str
    store_key: str = "spec"  # Key under which to store the file content

class GenerateCodeConfig(BaseModel):
    """Configuration for GenerateCodeStep"""
    input_key: str = "spec"  # Key in context where the specification is stored
    output_key: str = "codegen_result"  # Key to store the generated code result

class WriteFileConfig(BaseModel):
    """Configuration for WriteFileStep"""
    input_key: str = "codegen_result"  # Key in context where the codegen result is stored
    output_root: str  # Root directory where files will be written
```

### Recipe Model

```python
class RecipeStep(BaseModel):
    """A single step in a recipe"""
    type: str
    config: dict

class Recipe(BaseModel):
    """A complete recipe with multiple steps"""
    steps: List[RecipeStep]
```

## Integration Points

The Models component integrates with:

1. **Steps**: Step classes use configuration models to validate their inputs
2. **LLM**: The LLM component returns FileGenerationResult instances
3. **Executor**: The executor validates recipe structure against the Recipe model

## Validation Requirements

Models should validate:

1. File paths are strings (not path objects)
2. Required fields are present (e.g., path, content in FileSpec)
3. Lists are properly typed (e.g., files is a List[FileSpec])

## Future Considerations

1. Version field for recipe format evolution
2. Metadata fields for tracking and attribution
3. Support for file modes and encoding options
4. Dependencies between steps
