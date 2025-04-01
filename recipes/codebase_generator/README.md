# Codebase Generator

## Overview

The Codebase Generator is a simple but powerful recipe for generating code from specifications. It implements a minimalist approach to code generation, focusing on the core functionality needed to transform a specification into working code.

## Key Features

1. **Specification-Driven Code Generation**: Generate code directly from markdown specifications
2. **Implementation Philosophy**: Code follows a consistent philosophy favoring simplicity and clarity
3. **Support for Multiple Languages**: Configurable to generate code in different programming languages
4. **Optional Documentation Integration**: Can incorporate usage documentation into the generation process
5. **Existing Code Awareness**: Can consider existing code when provided

## How It Works

The Codebase Generator follows a simple three-step process:

1. **Read Implementation Philosophy**: Loads the implementation philosophy which guides the code generation
2. **Generate Code**: Uses an LLM to transform the specification into code that follows the implementation philosophy
3. **Write Output**: Writes the generated code to the specified output location

## Usage Instructions

To generate code from a specification:

```bash
python recipe_executor/main.py recipes/codebase_generator/generate_code.json \
  --context spec="Your component specification here" \
  --context component_id=your_component \
  --context output_path=path/to/output
```

### Required Parameters

- `spec`: The specification text for the component
- `component_id`: Identifier for the component being generated

### Optional Parameters

- `output_path`: Path where generated code should be placed (default: current directory)
- `language`: Programming language to generate (default: `python`)
- `model`: LLM model to use (default: `openai:o3-mini`)
- `existing_code`: Existing code to consider (if any)
- `usage_doc`: Usage documentation to indicate what must be implemented
- `additional_content`: Any additional content to include in the prompt
- `output_root`: Base directory for output files (default: `output`)

## Implementation Philosophy

The Codebase Generator follows a philosophy of ruthless simplicity, favoring:

- Minimal implementations that do exactly what's needed
- Clear, readable code over clever solutions
- Direct approaches with minimal abstraction
- Code that is easy to understand and maintain

For more details, see the [IMPLEMENTATION_PHILOSOPHY.md](includes/IMPLEMENTATION_PHILOSOPHY.md) file.

## Example

```bash
python recipe_executor/main.py recipes/codebase_generator/generate_code.json \
  --context spec="Create a function that validates email addresses using regex and returns a boolean result, \
    provide a main for passing an arg to the function and printing the result ." \
  --context component_id=email_validator \
  --context output_path=utils
```

This will generate an email validation utility in `output/utils/email_validator.py`.

## Integration with Other Recipes

The Codebase Generator is designed to be used as a component in larger generation workflows:

### Recipe Executor Self-Generation

The Recipe Executor project itself uses the codebase generator for its own component generation via `build_component.json`. This demonstrates a powerful real-world example of complex recipe composition:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/specs{{component_path}}/{{component_id}}.md",
      "artifact": "spec"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs{{component_path}}/{{component_id}}.md",
      "artifact": "usage_doc",
      "optional": true
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/codebase_generator/generate_code.json",
      "context_overrides": {
        "model": "openai:o3-mini",
        "output_root": "output",
        "output_path": "recipe_executor{{component_path}}",
        "language": "python",
        "spec": "{{spec}}",
        "usage_doc": "{{usage_doc}}",
        "existing_code": "{{existing_code}}",
        "additional_content": "{{additional_content}}"
      }
    }
  ]
}
```

This pattern shows how to:

1. Read specifications and documentation
2. Execute the codebase generator with specific context overrides
3. Build a complete system through composition of recipes
