# Recipe Executor

A robust, code-driven tool for executing LLM "recipes" using pydantic-ai. This tool can process structured recipes defined in YAML or JSON, as well as natural language recipes.

## Features

- **Natural Language Recipe Parsing** - Convert natural language instructions into structured recipes
- **Multiple Recipe Formats** - Support for YAML, JSON, and Markdown-based recipes
- **Rich Step Types** - LLM generation, file operations, Python execution, and more
- **Robust Error Handling** - Retries, timeouts, and graceful degradation
- **Validation Framework** - Ensure outputs match expectations
- **Variable Scoping** - Proper variable isolation and inheritance
- **Event System** - Track progress and monitor execution
- **Caching** - Optional caching of LLM responses for efficiency

## Installation

### Prerequisites

- Python 3.9+
- pip or conda for package management

### Install from source

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/recipe-executor.git
   cd recipe-executor
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Basic Usage

### Running a recipe from the command line

```bash
python recipe_executor.py path/to/recipe.yaml --output-dir ./outputs
```

### Optional command line arguments

```bash
python recipe_executor.py recipe_file [options]

options:
  --model MODEL           Default model to use (default: claude-3-7-sonnet-20250219)
  --provider PROVIDER     Default model provider (default: anthropic)
  --recipes-dir DIR       Directory containing recipe files (default: recipes)
  --output-dir DIR        Directory to output generated files to (default: output)
  --cache-dir DIR         Directory for caching LLM responses (default: cache)
  --temp TEMP             Default temperature setting (default: 0.1)
  --vars NAME=VALUE       Initial variables in the format name=value
  --validation LEVEL      Validation level: minimal, standard, strict (default: standard)
  --interaction MODE      Interaction mode: none, critical, regular, verbose (default: critical)
  --log-level LEVEL       Logging level: debug, info, warning, error (default: info)
```

### Using as a library

```python
import asyncio
from recipe_executor import RecipeExecutor

async def run_recipe():
    executor = RecipeExecutor(
        default_model_name="claude-3-7-sonnet-20250219",
        default_model_provider="anthropic",
        output_dir="./outputs"
    )

    # Load and execute a structured recipe
    recipe = await executor.load_recipe("my_recipe.yaml")
    result = await executor.execute_recipe(recipe)

    # Or execute a natural language recipe
    with open("natural_language_recipe.md", "r") as f:
        nl_content = f.read()
    result = await executor.parse_and_execute_natural_language(nl_content)

    print(f"Recipe status: {result.status}")

if __name__ == "__main__":
    asyncio.run(run_recipe())
```

## Recipe Formats

### YAML Recipe (Structured)

```yaml
metadata:
  name: "Example Recipe"
  description: "A simple example recipe"

model:
  provider: "anthropic"
  model_name: "claude-3-7-sonnet-20250219"

variables:
  input_file: "data.txt"

steps:
  - id: "read_data"
    name: "Read Input Data"
    type: "file_read"
    file_read:
      path: "${input_file}"
      as_variable: "content"

  - id: "analyze_data"
    name: "Analyze Data"
    type: "llm_generate"
    llm_generate:
      prompt: "Analyze this data: ${content}"
      output_variable: "analysis"
      output_format: "text"
```

### Natural Language Recipe

Natural language recipes can be written in plain text, describing the steps you want to execute. The system will parse these into structured recipes automatically.

Example:

```
# Customer Segmentation Analysis

I need a recipe that analyzes my customer data to identify key segments and create visualizations that help me understand my customer base better. Here's what I want to do:

1. Load my customer data from "customer_data.csv" which contains demographics, purchase history, and behavioral information.

2. Clean the data by:
   - Removing any duplicate records
   - Handling missing values appropriately (fill or remove)
   - Converting data types as needed

3. [... more steps...]
```

## Step Types

The system supports the following step types:

### LLM Generation (`llm_generate`)

Generate content using an LLM.

```yaml
llm_generate:
  prompt: "Write a summary of this text: ${text}"
  model: "claude-3-7-sonnet-20250219" # Optional override
  output_format: "text" # text, json, structured, files
  output_variable: "summary"
  temperature: 0.1 # Optional
  include_history: false # Whether to include previous messages
```

### File Reading (`file_read`)

Read file(s) from disk.

```yaml
file_read:
  path: "./data/input.txt"
  pattern: "*.csv" # Optional, for multiple files
  encoding: "utf-8"
  as_variable: "file_content"
```

### File Writing (`file_write`)

Write content to a file.

```yaml
file_write:
  path: "./output/result.txt"
  content_variable: "content"
  encoding: "utf-8"
  mode: "w" # w for write, a for append
  mkdir: true # Create directories if needed
```

### Template Substitution (`template_substitute`)

Substitute variables in a template.

```yaml
template_substitute:
  template: "Hello ${name}, welcome to ${company}!"
  template_file: "./templates/welcome.txt" # Alternative to inline template
  variables:
    name: "user_name"
    company: "company_name"
  output_variable: "welcome_message"
```

### JSON Processing (`json_process`)

Process JSON data.

```yaml
json_process:
  input_variable: "input_json"
  operations:
    - type: "extract"
      path: "data.items"
    - type: "filter"
      field: "status"
      value: "active"
  output_variable: "processed_json"
```

### Python Execution (`python_execute`)

Execute Python code.

```yaml
python_execute:
  code: |
    import datetime
    result = {"timestamp": datetime.datetime.now().isoformat(), "data": input_data}
  code_file: "./scripts/process.py" # Alternative to inline code
  input_variables:
    input_data: "data"
  output_variable: "result"
```

### Conditional Execution (`conditional`)

Execute a step conditionally.

```yaml
conditional:
  condition: "len(data) > 0"
  true_step:
    id: "process_data"
    type: "llm_generate"
    llm_generate:
      prompt: "Process this data: ${data}"
      output_variable: "processed_data"
  false_step:
    id: "handle_empty"
    type: "python_execute"
    python_execute:
      code: "result = {'error': 'No data available'}"
      output_variable: "error_result"
```

### Chain Execution (`chain`)

Execute a sequence of steps.

```yaml
chain:
  steps:
    - id: "step1"
      type: "file_read"
      file_read:
        path: "input.txt"
        as_variable: "content"
    - id: "step2"
      type: "llm_generate"
      llm_generate:
        prompt: "Analyze: ${content}"
        output_variable: "analysis"
  output_variable: "chain_result"
```

### Parallel Execution (`parallel`)

Execute steps in parallel.

```yaml
parallel:
  steps:
    - id: "task1"
      type: "llm_generate"
      llm_generate:
        prompt: "Task 1"
        output_variable: "result1"
    - id: "task2"
      type: "llm_generate"
      llm_generate:
        prompt: "Task 2"
        output_variable: "result2"
  output_variable: "parallel_results"
```

### Validation (`validator`)

Validate data against a schema or custom rules.

```yaml
validator:
  target_variable: "data"
  validation_type: "schema" # schema, code, llm
  schema: { /* JSON schema */ }
  output_variable: "validation_result"
```

### Wait for Input (`wait_for_input`)

Wait for user input.

```yaml
wait_for_input:
  prompt: "Please enter your name:"
  output_variable: "user_name"
  default_value: "Guest"
```

### API Call (`api_call`)

Make an HTTP API call.

```yaml
api_call:
  url: "https://api.example.com/data"
  method: "GET" # GET, POST, PUT, DELETE, PATCH
  headers:
    Authorization: "Bearer ${api_token}"
  data_variable: "request_data"
  output_variable: "api_response"
```

## Examples

The repository includes several example recipes:

- `natural-language-recipe.md` - Competitor analysis research tool
- `data-recipe.md` - Customer segmentation analysis
- `multimodal-recipe.md` - Product launch campaign creator
- `structured-yaml-recipe.yaml` - Text summarization pipeline

To run an example:

```bash
python recipe_executor.py examples/structured-yaml-recipe.yaml
```

## Advanced Features

### Variable Interpolation

You can use `${variable_name}` syntax to interpolate variables anywhere in your recipe:

```yaml
prompt: "Analyze this text: ${content}"
path: "${output_dir}/${filename}.txt"
```

### Nested Variable Access

Access nested properties using dot notation:

```yaml
prompt: "The user's name is ${user.profile.name}"
```

### Conditional Step Execution

Control whether a step runs based on a condition:

```yaml
condition: "len(data) > 0 and 'error' not in data"
```

### Error Handling and Retries

Configure how errors are handled and retries are performed:

```yaml
continue_on_error: true
retry_count: 3
retry_delay: 1
```

### Timeouts

Set timeouts for steps or the entire recipe:

```yaml
timeout: 60 # 60 seconds
```

## Troubleshooting

### Common Issues

1. **Missing dependencies**

   Ensure all required packages are installed:

   ```bash
   pip install -r requirements.txt
   ```

2. **API key configuration**

   For LLM providers, set the appropriate environment variables:

   - Anthropic: `ANTHROPIC_API_KEY`
   - OpenAI: `OPENAI_API_KEY`

3. **ValidationError in recipe**

   Check your recipe structure against the examples and ensure all required fields are present.

4. **Step execution failure**

   Enable debug logging for more details:

   ```bash
   python recipe_executor.py recipe.yaml --log-level debug
   ```

### Logs

Logs are written to the `logs` directory with a timestamp in the filename. Check these logs for detailed error information.

## License

MIT
