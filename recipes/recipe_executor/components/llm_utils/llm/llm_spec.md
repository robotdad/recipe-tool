# LLM Component Specification

## Purpose

The LLM component provides a unified interface for interacting with various large language model providers and optional MCP servers. It handles model initialization, request formatting, and result processing, enabling the Recipe Executor to generate content and orchestrate external tools through a single API.

## Core Requirements

- Support multiple LLM providers (Azure OpenAI, OpenAI, Anthropic, Ollama)
- Provide model initialization based on a standardized model identifier format
- Encapsulate LLM API details behind a unified interface
- Use PydanticAI's async interface for non-blocking LLM calls
- Use PydanticAI for consistent handling and validation of LLM output
- Implement basic error handling
- Support optional structured output format
- Accept an optional `mcp_servers: Optional[List[MCPServer]]` to enable remote MCP tool integration

## Implementation Considerations

- Use a clear `provider/model_name` identifier format
- Do not need to pass api keys directly to model classes
  - Exception: need to provide to AzureProvider)
- Use PydanticAI's provider-specific model classes, passing only the model name
  - pydantic_ai.models.openai.OpenAIModel (used also for Azure OpenAI and Ollama)
  - pydantic_ai.models.anthropic.AnthropicModel
- Create a PydanticAI Agent with the model, structured output type, and optional MCP servers
- Support: `output_type: Type[Union[str, BaseModel]] = str`
- Pass provided `mcp_servers` (or empty list) to the Agent constructor (e.g. `Agent(model, mcp_servers=mcp_servers, output_type=output_type)`)
- Implement fully asynchronous execution:
  - Make `generate` an async function (`async def generate`)
  - Use `await agent.run(prompt)` method of the Agent to make requests
- CRITICAL: make sure to return the `result.output` in the `generate` method to return only the structured output

## Logging

- Debug: Log full request payload before making call and then full result payload after receiving it, making sure to mask any sensitive information (e.g. API keys, secrets, etc.)
- Info: Log model name and provider before making call (do not include the request payload details) and then include processing times and tokens used upon completion (do not include the result payload details)

## Component Dependencies

### Internal Components

- **Azure OpenAI**: Uses `get_azure_openai_model` for Azure OpenAI model initialization
- **Logger**: Uses the logger for logging LLM calls
- **MCP**: Integrates remote MCP tools when `mcp_servers` are provided (uses `pydantic_ai.mcp`)

### External Libraries

- **pydantic-ai**: Uses PydanticAI for model initialization, Agent-based request handling, and structured-output processing
- **pydantic-ai.mcp**: Provides `MCPServer`, `MCPServerHTTP` and `MCPServerStdio` classes for MCP server transports

### Configuration Dependencies

- **DEFAULT_MODEL**: (Optional) Environment variable specifying the default LLM model in format "provider/model_name"
- **OPENAI_API_KEY**: (Required for OpenAI) API key for OpenAI access
- **ANTHROPIC_API_KEY**: (Required for Anthropic) API key for Anthropic access
- **OLLAMA_BASE_URL**: (Required for Ollama) Endpoint for Ollama models

## Error Handling

- Provide clear error messages for unsupported providers
- Handle network and API errors gracefully
- Log detailed error information for debugging

## Output Files

- `recipe_executor/llm_utils/llm.py`

## Dependency Integration Considerations

### PydanticAI

Create a PydanticAI model for the LLM provider and model name. This will be used to initialize the model and make requests.

```python
def get_model(model_id: str) -> OpenAIModel | AnthropicModel:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider/model_name' or 'provider/model_name/deployment_name'.

    Supported providers:
    - openai
    - azure (for Azure OpenAI, use 'azure/model_name/deployment_name' or 'azure/model_name')
    - anthropic
    - ollama

    Args:
        model_id (str): Model identifier in format 'provider/model_name'
            or 'provider/model_name/deployment_name'.
            If None, defaults to 'openai/gpt-4o'.

    Returns:
        The model instance for the specified provider and model.

    Raises:
        ValueError: If model_id format is invalid or if the provider is unsupported.
    """

    # If 'azure' is the model provider, use the `get_azure_openai_model` function
```

Usage example:

```python
# Get an OpenAI model
openai_model = get_model("openai/o4-mini")
# Uses OpenAIModel('o4-mini')

# Get an Anthropic model
anthropic_model = get_model("anthropic/claude-3-7-sonnet-latest")
# Uses AnthropicModel('claude-3-7-sonnet-latest')

# Get an Ollama model
ollama_model = get_model("ollama/phi4")
# Uses OllamaModel('phi4')
```

Getting an agent:

```python
from pydantic_ai import Agent

# Create an agent with the model
agent: Agent[None, Union[str, BaseModel]] = Agent(model=ollama_model, output_type=str, mcp_servers=mcp_servers)

# Call the agent with a prompt
async with agent.run_mcp_servers():
  result = await agent.run("What is the capital of France?")

# Process the result
print(result.data)  # This will print the structured output
```

#### Ollama

- The Ollama model requires an endpoint to be specified. This can be done by passing the `endpoint` parameter to the `get_model` function.
- The endpoint should be in the format `http://<host>:<port>`, where `<host>` is the hostname or IP address of the Ollama server and `<port>` is the port number on which the server is running.

Then you can use the `OpenAIModel` class to create an instance of the model and make requests to the Ollama server.

```python
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers import OpenAIProvider
import dotenv
import os

# Load environment variables from .env file
dotenv.load_dotenv()
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

# inside the get_model function
return OpenAIModel(
    model_name='qwen2.5-coder:7b',
    provider=OpenAIProvider(base_url=f'{OLLAMA_BASE_URL}/v1'),
)
```
