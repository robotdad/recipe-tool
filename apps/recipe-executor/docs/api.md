# API Documentation

Recipe Executor Gradio App provides a clean API to interact with recipe execution and creation programmatically.

## API Endpoints

The app exposes three named API endpoints:

1. `execute_recipe` - Execute a recipe
2. `create_recipe` - Create a recipe from a description
3. `load_example` - Load an example recipe

## Using the API

You can interact with the API using the [Gradio Client](https://www.gradio.app/guides/getting-started-with-the-python-client) or any HTTP client.

### Python Client Example

```python
from gradio_client import Client

client = Client("http://127.0.0.1:[PORT]")  # Replace [PORT] with the actual port

# You can call predict() with specific parameters
# or view API details with client.view_api()
```

## API Details

### execute_recipe

Executes a recipe and returns the results.

**Parameters:**

- `recipe_file`: Optional path to a recipe JSON file (upload a file or pass `None`)
- `recipe_text`: Optional JSON string containing the recipe (pass `None` if using a file)
- `context_vars`: Optional comma-separated key=value pairs (e.g., "key1=value1,key2=value2"). Note that `recipe_root`, `ai_context_root`, and `output_root` are automatically provided.

**Returns:**

A dictionary with the following keys:

- `formatted_results`: Markdown-formatted results
- `raw_json`: Raw JSON results

**Example:**

```python
from gradio_client import Client

client = Client("http://127.0.0.1:[PORT]")  # Replace [PORT] with the actual port

result = client.predict(
    None,                      # recipe_file
    '{"name": "Test Recipe", "steps": [{"type": "set_context", "config": {"key": "greeting", "value": "Hello, World!"}}]}',
    "name=Recipe Executor",    # context_vars
    api_name="execute_recipe"
)

print(result["formatted_results"])  # Markdown formatted results
print(result["raw_json"])           # Raw JSON output
```

### create_recipe

Creates a new recipe from an idea description.

**Parameters:**

- `idea_text`: Text describing the recipe idea (pass `None` if using a file)
- `idea_file`: Optional path to a file containing the recipe idea (pass `None` if using text)
- `reference_files`: Optional list of reference file paths
- `context_vars`: Optional comma-separated key=value pairs. Note that `recipe_root`, `ai_context_root`, and `output_root` are automatically provided.

**Returns:**

A dictionary with the following keys:

- `recipe_json`: The generated recipe JSON
- `structure_preview`: Markdown preview of the recipe structure

**Example:**

```python
from gradio_client import Client

client = Client("http://127.0.0.1:[PORT]")  # Replace [PORT] with the actual port

result = client.predict(
    "Create a recipe that reads a file and extracts email addresses",  # idea_text
    None,                                                             # idea_file
    None,                                                             # reference_files
    "model=gpt-4",                                                    # context_vars
    api_name="create_recipe"
)

print(result["recipe_json"])          # Generated JSON recipe
print(result["structure_preview"])    # Markdown structure preview
```

### load_example

Loads an example recipe.

**Parameters:**

- `example_path`: Path to an example recipe

**Returns:**

A dictionary with the following keys:

- `recipe_content`: The loaded recipe JSON
- `description`: Description of the example

**Example:**

```python
from gradio_client import Client

client = Client("http://127.0.0.1:[PORT]")  # Replace [PORT] with the actual port

result = client.predict(
    "../../recipes/example_simple/test_recipe.json",  # example_path
    api_name="load_example"
)

print(result["recipe_content"])  # Recipe JSON
print(result["description"])     # Example description
```

## HTTP API

For direct HTTP calls, you can use the JSON API:

```bash
# Execute a recipe
curl -X POST http://127.0.0.1:[PORT]/api/execute_recipe  # Replace [PORT] with the actual port \
  -H "Content-Type: application/json" \
  -d '{"data": [null, "{\"name\": \"Test Recipe\"}", "key=value"]}'

# Create a recipe
curl -X POST http://127.0.0.1:[PORT]/api/create_recipe  # Replace [PORT] with the actual port \
  -H "Content-Type: application/json" \
  -d '{"data": ["Create a simple recipe", null, null, null]}'

# Load an example
curl -X POST http://127.0.0.1:[PORT]/api/load_example  # Replace [PORT] with the actual port \
  -H "Content-Type: application/json" \
  -d '{"data": ["../../recipes/example_simple/test_recipe.json"]}'
```

## JavaScript Client

You can also use the Gradio JavaScript client:

```javascript
import { client } from "@gradio/client";

async function executeRecipe() {
  const app = await client("http://127.0.0.1:[PORT]/"); // Replace [PORT] with the actual port

  const result = await app.predict("/execute_recipe", [
    null, // recipe_file
    '{"name": "Test Recipe"}', // recipe_text
    "key1=value1", // context_vars
  ]);

  console.log(result.data);
}

executeRecipe();
```
