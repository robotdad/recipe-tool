# Recipe Tool

**Transform natural language ideas into reliable, automated workflows** - Recipe Tool bridges the gap between human intent and executable automation. Write what you want to accomplish in plain English, and Recipe Tool generates the JSON recipe that makes it happen - reproducibly and reliably.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## What is Recipe Tool?

Recipe Tool is a command-line interface that combines **recipe creation** with **recipe execution**, turning natural language descriptions into automated workflows. Think of it as a compiler that translates your ideas into reliable, repeatable automation.

**Key Capabilities:**
- 🧠 **Natural Language to Code** - Describe your workflow in plain English/Markdown
- 🔄 **Reliable Execution** - Generated recipes run deterministically every time
- 🤖 **Multi-LLM Support** - Works with OpenAI, Anthropic, Azure OpenAI, Ollama
- 🛠️ **Rich Step Types** - File operations, conditionals, loops, parallel execution
- 🔗 **Tool Integration** - MCP (Model Context Protocol) server support
- 📊 **Structured Output** - Generate JSON, code, documents, reports

## The Recipe Tool Workflow

Recipe Tool follows a simple but powerful workflow:

### 1. Write Your Idea
Start with a natural language description of what you want to accomplish:

```markdown
# Code Quality Analyzer

Read all Python files in the project and:

1. Count lines of code per file
2. Identify files with no docstrings
3. Check for TODO/FIXME comments
4. Create a comprehensive report with recommendations
```

### 2. Generate a Recipe
Transform your idea into an executable JSON recipe:

```bash
recipe-tool --create code_analyzer_idea.md
# Creates: output/code_quality_analyzer.json
```

### 3. Execute Reliably
Run your recipe with consistent, reproducible results:

```bash
recipe-tool --execute output/code_quality_analyzer.json project_path=./my-project
```

## Installation

```bash
pip install recipe-tool
```

**Note:** Recipe Tool automatically installs `recipe-executor` as a dependency, giving you both creation and execution capabilities.

## Quick Start

### Basic Usage

1. **Create a simple idea file** (`hello_world.md`):
```markdown
# Hello World Generator

Create a Python script that prints "Hello, World!" and save it to a file.
```

2. **Generate the recipe**:
```bash
recipe-tool --create hello_world.md
```

3. **Execute the generated recipe**:
```bash
recipe-tool --execute output/hello_world_generator.json
```

### Environment Setup

Configure your LLM provider:

```bash
# OpenAI
export OPENAI_API_KEY="your-api-key"

# Anthropic
export ANTHROPIC_API_KEY="your-api-key"

# Azure OpenAI
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_BASE_URL="https://your-resource.openai.azure.com/"
```

## What Gets Generated

When you describe a task, Recipe Tool creates a JSON recipe with structured steps. Here's what gets generated for a file summarization task:

**Your Idea:**
```markdown
# File Summarizer
Read a text file and create a summary of its contents.
```

**Generated Recipe:**
```json
{
  "name": "file_summarizer",
  "steps": [
    {
      "step_type": "read_files",
      "paths": ["{{ input_file }}"]
    },
    {
      "step_type": "llm_generate",
      "prompt": "Create a concise summary of this content:\n\n{{ file_contents[0] }}",
      "model": "gpt-4o"
    },
    {
      "step_type": "write_files",
      "files": [
        {
          "path": "{{ output_file }}",
          "content": "# Summary\n\n{{ llm_output }}"
        }
      ]
    }
  ]
}
```

## Advanced Examples

### Multi-Step Document Processing

```markdown
# Research Report Generator

1. Read a list of URLs from a file
2. Fetch content from each URL
3. Generate summaries for each source
4. Combine summaries into a comprehensive report
5. Format as markdown with citations
```

```bash
recipe-tool --create research_report.md
recipe-tool --execute output/research_report_generator.json \
  urls_file=sources.txt output_file=research_report.md
```

### Code Generation from Specifications

```markdown
# API Client Generator

Given an API specification file:
1. Parse the API endpoints and schemas
2. Generate Python client code with proper error handling
3. Create unit tests for the client
4. Generate documentation with usage examples
```

```bash
recipe-tool --create api_client_generator.md
recipe-tool --execute output/api_client_generator.json \
  spec_file=api_spec.yaml output_dir=generated_client/
```

### Batch File Processing

```markdown
# Image Processing Pipeline

For all images in a directory:
1. Resize to multiple dimensions (thumbnail, medium, large)
2. Optimize file sizes
3. Generate metadata JSON files
4. Create an index HTML file with image gallery
```

```bash
recipe-tool --create image_processor.md
recipe-tool --execute output/image_processing_pipeline.json \
  input_dir=raw_images/ output_dir=processed/
```

## CLI Reference

### Core Commands

```bash
# Create a recipe from natural language
recipe-tool --create IDEA_FILE

# Execute an existing recipe
recipe-tool --execute RECIPE_FILE [CONTEXT_VARS...]

# Show help
recipe-tool --help
```

### Options

```bash
--log-dir DIR           Directory for log files (default: logs)
--debug                 Enable debug mode with breakpoints
```

### Context Variables

Pass variables to recipes:

```bash
recipe-tool --execute recipe.json \
  input_file=data.txt \
  output_dir=results/ \
  model=gpt-4o \
  temperature=0.3
```

## Recipe Ecosystem

Recipe Tool is part of a larger ecosystem:

- **recipe-executor** - Core execution engine (auto-installed)
- **recipe-tool** - This package - adds creation capabilities
- **recipe-tool-app** - Web interface for visual recipe management
- **MCP servers** - Integration with AI assistants like Claude

## Web Interface

For a visual experience, install and run the web interface:

```bash
# Install the web app (separate package)
pip install recipe-tool-app

# Launch the interface
recipe-tool-app
```

Features:
- Visual recipe creation and editing
- Real-time execution with step-by-step output
- Example recipe browser
- Context variable management
- File upload and download

## Integration with AI Assistants

Recipe Tool provides MCP (Model Context Protocol) integration for AI assistants:

```bash
# For Claude Desktop
recipe-tool-mcp-server stdio

# For HTTP clients
recipe-tool-mcp-server sse --port 3002
```

This allows AI assistants to:
- Create recipes from your conversations
- Execute workflows on your behalf
- Iterate on recipes based on results

## Use Cases

Recipe Tool excels at:

### 📝 Content Generation
- Blog posts, documentation, reports
- Code generation from specifications
- Template-based content creation

### 🔧 Automation Workflows
- File processing and transformation
- API integration and data collection
- Batch operations and data migration

### 🧪 Research & Analysis
- Data analysis and visualization
- Web scraping and content aggregation
- Competitive analysis and reporting

### 💻 Development Tasks
- Code generation and scaffolding
- Test data creation
- Documentation generation

## Philosophy: More Code Than Model

Recipe Tool follows a "more code than model" philosophy:

- **LLM for Creation** - Use AI to generate the recipe from your idea
- **Deterministic Execution** - Run the recipe with consistent, reliable results
- **Reproducible Workflows** - Same inputs always produce same outputs
- **Version Control Ready** - Recipes are JSON files that can be tracked and shared

This approach gives you the creativity and accessibility of AI with the reliability and reproducibility of traditional automation.

## Python API

Use Recipe Tool programmatically:

```python
from recipe_tool.app import create_recipe, execute_recipe

# Create a recipe from text
recipe_json = await create_recipe(
    idea="Generate a Python class for user management",
    reference_files=["user_model.py"]
)

# Execute the recipe
result = await execute_recipe(
    recipe_json,
    context={"class_name": "UserManager"}
)
```

## Error Handling

Recipe Tool provides comprehensive error handling:

- **Creation Errors** - Clear feedback on malformed ideas or missing context
- **Execution Errors** - Step-by-step error reporting with context
- **Validation** - Recipe validation before execution
- **Logging** - Detailed logs for debugging and audit trails

## Part of Recipe Tool Ecosystem

Recipe Tool is part of the larger [Recipe Tool Project](https://github.com/microsoft/recipe-tool):

- **Full Documentation** - Comprehensive guides and examples
- **Example Recipes** - Pre-built recipes for common tasks
- **Community Recipes** - Shared recipes and patterns
- **Advanced Features** - Self-generating code, parallel execution, MCP integration

For advanced usage, complex examples, and the full ecosystem, visit the [Recipe Tool repository](https://github.com/microsoft/recipe-tool).

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/microsoft/recipe-tool/blob/main/LICENSE) file for details.

## Support

This is an experimental project from Microsoft. For issues and examples:
- [GitHub Repository](https://github.com/microsoft/recipe-tool)
- [Example Recipes](https://github.com/microsoft/recipe-tool/tree/main/recipes)
- [Documentation](https://github.com/microsoft/recipe-tool/blob/main/README.md)
- [Web Interface](https://pypi.org/project/recipe-tool-app/) (separate package)