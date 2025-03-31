# Recipe Executor Documentation

## Overview

Recipe Executor is a flexible orchestration system for executing recipe-based workflows that generate and manipulate code and other files. The system is designed around JSON recipe files that define sequential steps for tasks like reading files, generating content with LLMs, and writing output files.

## System Architecture

Recipe Executor follows a modular architecture with these key components:

1. **Recipe Format**: JSON-based definitions that specify a sequence of steps
2. **Executor**: Central orchestration engine that loads recipes and executes steps
3. **Context**: Shared state container for passing data between steps
4. **Step Types**: Various operations including file I/O and LLM generation
5. **LLM Integration**: Connectors to language model services

## Core Concepts

### Recipes

Recipes are JSON files that define a sequence of steps to be executed. They can be standalone or reference other recipes through the `execute_recipe` step.

Basic recipe structure:
```json
{
  "steps": [
    {
      "type": "step_type",
      "param1": "value1",
      "param2": "value2"
    }
  ]
}
```

### Step Types

1. **read_file**: Reads content from a file
2. **generate**: Generates content using an LLM
3. **write_file**: Writes content to files 
4. **execute_recipe**: Runs another recipe (enables recipe composition)

### Context System

The context is a shared state container that passes data between steps. It's dictionary-like and stores:
- Artifacts (content read or generated)
- Configuration values

### Template System

Recipe Executor uses Liquid templates for dynamic content generation:
- Template variables in double curly braces: `{{ variable }}`
- Supports conditionals: `{% if condition %}...{% endif %}`
- Templates are rendered using context values

## Creating Custom Projects

### Project Structure

When creating your own projects with Recipe Executor:

1. **Define specifications**: Create markdown files describing component requirements
2. **Create recipe files**: JSON files that orchestrate the generation process
3. **Organize in folders**: Group related files by component

### Recipe Writing Guidelines

1. **Start with the end in mind**: Define what files you want to create
2. **Break down into steps**: 
   - Read specification files
   - Generate code with appropriate prompts
   - Write output files
3. **Use templating**: Templates enable dynamic content generation
4. **Compose recipes**: Use the execute_recipe step to create hierarchical workflows

### Workflow Patterns

1. **Blueprint Generation**: Validate specs → Generate blueprint → Create component
2. **Code Generation**: Read specs → Generate code → Write files
3. **Sequential Refinement**: Create → Edit → Test → Refine

## Extending the System

### Creating New Step Types

1. Create a new class extending `BaseStep`
2. Define a configuration class using Pydantic
3. Implement the `execute` method
4. Register the step in `steps/registry.py`

### Customizing LLM Integration

The `llm.py` module handles communication with language model services. Extend it to:
1. Add support for new providers
2. Customize prompting strategies
3. Implement specialized generation techniques

### Adding Template Functions

Enhance template rendering by adding custom filters and functions to the templating engine in `utils.py`.

## Project Bootstrapping

Recipe Executor can generate its own code, demonstrating its power for code generation:

1. **Create from scratch**: `make recipe-executor-create`
2. **Edit existing code**: `make recipe-executor-edit`

This self-bootstrapping capability highlights how the system can be used for complex code generation tasks.