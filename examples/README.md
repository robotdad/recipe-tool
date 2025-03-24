# Recipe Examples

This directory contains example recipes for the Recipe Executor.

## Available Examples

- `content_generator.yaml`: Generates an article based on a topic
- `content_analyzer.yaml`: Analyzes a collection of articles and generates a report
- `data_visualization.yaml`: Processes data and creates visualizations
- `api_workflow.yaml`: Demonstrates a workflow with API calls
- `parallel_processing.yaml`: Shows how to use parallel execution
- `conditional_logic.yaml`: Demonstrates conditional execution
- `interactive_workflow.md`: An example recipe in markdown format with user interaction

## Running Examples

You can run these examples using the command line:

```bash
recipe-executor examples/content_generator.yaml
```

Or using the Python API:

```python
import asyncio
from recipe_executor import RecipeExecutor

async def main():
    executor = RecipeExecutor()
    recipe = await executor.load_recipe("examples/content_generator.yaml")
    result = await executor.execute_recipe(recipe)
    print(f"Recipe execution status: {result.status}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Creating Your Own Recipes

Use these examples as templates for creating your own recipes. You can:

1. Copy and modify an existing recipe file
2. Create a new recipe in YAML, JSON, or Markdown format
3. Define a recipe in natural language and let the Recipe Executor convert it

See the main documentation for detailed information on recipe structure and capabilities.
