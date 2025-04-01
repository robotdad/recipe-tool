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

Recipe Executor is built on just four core primitive operations:

1. **read_file**: Reads content from a file
2. **generate**: Generates content using an LLM
3. **write_file**: Writes content to files
4. **execute_recipe**: Runs another recipe (enables recipe composition)

These primitives are sufficient for most code generation workflows.

### Context System

The context is a shared state container that passes data between steps. It's dictionary-like and stores:

- Artifacts (content read or generated)
- Configuration values

### Template System

Recipe Executor uses Liquid templates for dynamic content generation:

- Template variables in double curly braces: `{{ variable }}`
- Supports conditionals: `{% if condition %}...{% endif %}`
- Templates are rendered using context values

## Recipe Configuration

### Default Configuration

Recipe Executor defaults to using OpenAI models. The default configuration in recipe files uses:

```json
"model": "openai:o3-mini"
```

This can be found in the following key recipe files:

- `/recipes/codebase_generator/generate_code.json`
- `/recipes/component_blueprint_generator/build_blueprint.json`
- `/recipes/recipe_executor/build_component.json`

### Using Multiple Model Providers

While OpenAI is now the default, Recipe Executor still supports other providers:

- Azure OpenAI: `azure:model_name:deployment_name` (e.g., `azure:gpt-4:my-deployment`)
- OpenAI: `openai:model_name` (e.g., `openai:gpt-4o`, `openai:o3-mini`)
- Anthropic: `anthropic:model_name` (e.g., `anthropic:claude-3.7-sonnet-latest`)
- Gemini: `gemini:model_name` (e.g., `gemini:gemini-pro`)

### Overriding Model Selection

You can override the model selection in various ways:

1. **In Recipe Files**: Change the `model` parameter directly

   ```json
   "model": "azure:gpt-4:my-custom-deployment"
   ```

2. **Via Context Variables**: Pass a context variable when executing a recipe

   ```bash
   python recipe_executor/main.py path/to/recipe.json --context model=azure:gpt-4:my-deployment
   ```

3. **In Sub-recipe Context Overrides**: When executing sub-recipes
   ```json
   "context_overrides": {
     "model": "azure:gpt-4:my-deployment"
   }
   ```

## Recipe Writing Guidelines

1. **Start with the end in mind**: Define what files you want to create
2. **Break down into steps**:
   - Read specification files
   - Generate code with appropriate prompts
   - Write output files
3. **Use templating**: Templates enable dynamic content generation
4. **Compose recipes**: Use the execute_recipe step to create hierarchical workflows
