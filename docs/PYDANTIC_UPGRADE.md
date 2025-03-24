# Pydantic-AI Integration

This document explains the integration of pydantic-ai into the recipe-executor project.

## Overview

We've upgraded the natural language recipe parsing system to use pydantic-ai instead of the previous approach that relied on generating YAML as an intermediate format. This provides several key benefits:

1. **Direct Structured Output** - Instead of generating YAML that needs to be parsed, we directly generate validated Pydantic objects.
2. **Type Safety and Validation** - Pydantic-ai ensures LLM outputs conform to expected schemas with proper validation.
3. **Simplified Processing** - Removes an intermediate step, reducing potential errors.
4. **Model Agnostic** - Works with multiple LLM providers including Anthropic, OpenAI, Google, Mistral, Ollama, and Groq.

## Implementation Changes

### 1. New Models

- Created `recipe_executor/models/pydantic_recipe.py` with Pydantic models for recipes that work with pydantic-ai.
- These models mirror the structure of the existing Recipe models but are designed to work directly with LLMs.

### 2. New Parser

- Added `recipe_executor/parsers/pydantic_parser.py` that uses pydantic-ai to parse natural language into structured recipes.
- The parser creates an Agent that uses the specified LLM to convert text directly to a Recipe object.

### 3. Updated Main Module

- Modified `_parse_natural_language_recipe()` in `main.py` to use the new parser.
- Added a conversion function to ensure compatibility with existing code while we transition.

## Architecture

The new workflow is:

1. User provides natural language recipe description
2. `RecipeParser` creates a pydantic-ai Agent with the appropriate model
3. Agent converts natural language directly to a `Recipe` object
4. Recipe is executed normally

## Future Improvements

1. **Full Migration** - Gradually migrate all code to use pydantic-ai models directly without conversion.
2. **Tool Integration** - Utilize pydantic-ai tools for executing recipe steps.
3. **Streaming Results** - Implement streaming for large recipe outputs.
4. **Model Caching** - Better handling of model reuse for performance.

## Usage Example

```python
from recipe_executor.parsers.pydantic_parser import RecipeParser

# Create a parser with the default model
parser = RecipeParser()

# Parse a natural language recipe
recipe = await parser.parse_recipe_from_text("""
I need a system that can analyze text and extract key points.
First, read the input file, then use an LLM to analyze it,
and finally write the results to an output file.
""")

# The recipe is a structured object ready to be executed
print(recipe.metadata.name)
print(len(recipe.steps))
```