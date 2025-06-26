# Recipe Executor

**A Python execution engine for JSON-defined AI workflows** - Recipe Executor runs structured "recipes" that combine file operations, LLM interactions, and control flow into automated workflows. Perfect for AI-powered content generation, file processing, and complex automation tasks.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## What is Recipe Executor?

Recipe Executor is a pure execution engine that runs JSON "recipes" - structured workflow definitions that describe automated tasks. Think of it as a workflow engine specifically designed for AI-powered automation.

**Key Features:**
- 🤖 **Multi-LLM Support** - OpenAI, Anthropic, Azure OpenAI, Ollama
- 📁 **File Operations** - Read/write files with JSON/YAML parsing
- 🔄 **Control Flow** - Conditionals, loops, parallel execution
- 🛠️ **Tool Integration** - MCP (Model Context Protocol) server support
- 🎯 **Context Management** - Shared state across workflow steps
- ⚡ **Concurrent Execution** - Built-in parallelization and resource management

## Quick Start

### Installation

```bash
pip install recipe-executor
```

### Basic Usage

1. **Create a recipe** (JSON file):

```json
{
  "name": "summarize_file",
  "steps": [
    {
      "step_type": "read_files",
      "paths": ["{{ input_file }}"]
    },
    {
      "step_type": "llm_generate", 
      "prompt": "Summarize this content:\n\n{{ file_contents[0] }}"
    },
    {
      "step_type": "write_files",
      "files": [
        {
          "path": "summary.md",
          "content": "{{ llm_output }}"
        }
      ]
    }
  ]
}
```

2. **Execute the recipe**:

```bash
recipe-executor recipe.json --context input_file=document.txt
```

### Environment Setup

Configure your LLM providers via environment variables:

```bash
# OpenAI
export OPENAI_API_KEY="your-api-key"

# Anthropic  
export ANTHROPIC_API_KEY="your-api-key"

# Azure OpenAI
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_BASE_URL="https://your-resource.openai.azure.com/"
```

## Step Types

Recipe Executor provides 9 built-in step types:

### File Operations
- **`read_files`** - Read file content (supports JSON/YAML parsing, glob patterns)
- **`write_files`** - Write files to disk with automatic directory creation

### LLM Integration  
- **`llm_generate`** - Generate content using various LLM providers
  - Supports structured output (JSON schemas, file specifications)
  - MCP server integration for tool access
  - Built-in web search capabilities

### Control Flow
- **`conditional`** - Branch execution based on boolean conditions
- **`loop`** - Iterate over collections with optional concurrency
- **`parallel`** - Execute multiple steps concurrently
- **`execute_recipe`** - Execute nested recipes (composition)

### Context Management
- **`set_context`** - Set context variables and configuration  
- **`mcp`** - Direct MCP server interactions

## Example Recipes

### AI-Powered Code Generation

```json
{
  "name": "generate_python_class",
  "steps": [
    {
      "step_type": "llm_generate",
      "prompt": "Create a Python class for {{ class_description }}",
      "response_format": {
        "type": "json_schema",
        "json_schema": {
          "name": "code_generation",
          "schema": {
            "type": "object",
            "properties": {
              "code": {"type": "string"},
              "explanation": {"type": "string"}
            }
          }
        }
      }
    },
    {
      "step_type": "write_files",
      "files": [
        {
          "path": "{{ class_name }}.py", 
          "content": "{{ llm_output.code }}"
        }
      ]
    }
  ]
}
```

### Batch File Processing

```json
{
  "name": "process_documents",
  "steps": [
    {
      "step_type": "read_files",
      "paths": ["docs/*.txt"],
      "use_glob": true
    },
    {
      "step_type": "loop",
      "items": "{{ file_contents }}",
      "concurrency": 3,
      "steps": [
        {
          "step_type": "llm_generate",
          "prompt": "Extract key points from: {{ item }}"
        },
        {
          "step_type": "write_files", 
          "files": [
            {
              "path": "summaries/summary_{{ loop_index }}.md",
              "content": "{{ llm_output }}"
            }
          ]
        }
      ]
    }
  ]
}
```

## Advanced Features

### LLM Provider Configuration

```json
{
  "step_type": "llm_generate",
  "model": "gpt-4o",
  "provider": "openai",
  "max_tokens": 1000,
  "temperature": 0.7,
  "prompt": "Your prompt here"
}
```

### MCP Server Integration

```json
{
  "step_type": "llm_generate",
  "mcp_servers": [
    {
      "server_name": "web_search",
      "command": "mcp-server-web-search",
      "args": []
    }
  ],
  "tools": ["web_search"],
  "prompt": "Search for information about {{ topic }}"
}
```

### Conditional Execution

```json
{
  "step_type": "conditional",
  "condition": "file_exists('config.json')",
  "then_steps": [...],
  "else_steps": [...]
}
```

## CLI Reference

```bash
recipe-executor RECIPE_FILE [OPTIONS]

Options:
  --context KEY=VALUE    Context variables (can be used multiple times)
  --config KEY=VALUE     Configuration overrides (can be used multiple times)  
  --log-dir DIR         Directory for log files (default: logs)
```

**Examples:**

```bash
# Basic execution
recipe-executor workflow.json

# With context variables
recipe-executor workflow.json --context input=data.txt output=results/

# With configuration overrides
recipe-executor workflow.json --config model=gpt-4o --config temperature=0.3

# Custom log directory
recipe-executor workflow.json --log-dir ./execution-logs
```

## Python API

You can also use Recipe Executor programmatically:

```python
import asyncio
from recipe_executor.executor import Executor
from recipe_executor.models import Recipe
from recipe_executor.context import Context
from recipe_executor.logger import init_logger

async def run_recipe():
    # Load recipe
    with open("recipe.json") as f:
        recipe = Recipe.model_validate_json(f.read())
    
    # Create context
    context = Context(
        artifacts={"input": "Hello World"},
        config={"model": "gpt-4o"}
    )
    
    # Execute
    logger = init_logger("logs")
    executor = Executor(logger)
    await executor.execute(recipe, context)

asyncio.run(run_recipe())
```

## Error Handling

Recipe Executor provides comprehensive error handling:

- **Step-level isolation** - Errors in one step don't break the entire workflow
- **Detailed logging** - Structured logs with step-by-step execution details
- **Graceful failures** - Clear error messages with context information
- **Resource cleanup** - Automatic cleanup of temporary resources

## Part of Recipe Tool Ecosystem

Recipe Executor is the core execution engine of the larger [Recipe Tool](https://github.com/microsoft/recipe-tool) ecosystem:

- **recipe-tool** - CLI for creating and executing recipes from natural language
- **recipe-executor** - This package - pure execution engine
- **Document Generator App** - Web UI for document workflows
- **MCP Servers** - Integration with AI assistants like Claude

For more examples and advanced usage patterns, visit the [Recipe Tool repository](https://github.com/microsoft/recipe-tool).

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/microsoft/recipe-tool/blob/main/LICENSE) file for details.

## Support

This is an experimental project from Microsoft. For issues and examples:
- [GitHub Repository](https://github.com/microsoft/recipe-tool)
- [Example Recipes](https://github.com/microsoft/recipe-tool/tree/main/recipes)
- [Documentation](https://github.com/microsoft/recipe-tool/blob/main/README.md)