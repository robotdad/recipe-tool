# Azure OpenAI Integration Guide for Recipe Executor

This document outlines how to configure and use Recipe Executor with Azure OpenAI services.

## Configuration

### Environment Variables

To use Azure OpenAI with Recipe Executor, you need to set the following environment variables in your `.env` file:

```
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_USE_MANAGED_IDENTITY=false
```

**Notes:**
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI service endpoint URL
- `AZURE_OPENAI_API_KEY`: Your API key (not required if using managed identity)
- `AZURE_USE_MANAGED_IDENTITY`: Set to `true` to use Azure Managed Identity for authentication

### Authentication Methods

Recipe Executor supports two authentication methods for Azure OpenAI:

1. **API Key Authentication**: Default method using the API key provided in the environment variables
2. **Managed Identity Authentication**: Uses Azure Managed Identity for authentication without API keys, ideal for secure Azure environments

## Model Identifiers

When using Azure OpenAI, model identifiers follow this format:

```
azure:model_name:deployment_name
```

For example:
- `azure:gpt-4:deployment-gpt4`
- `azure:o3-mini:deployment-o3-mini`

These model identifiers are used in recipe files and when calling the LLM service directly.

## Recipe Configuration

### Default Configuration

Recipe Executor now defaults to using Azure OpenAI models. The default configuration in recipe files uses:

```json
"model": "azure:o3-mini"
```

This can be found in the following key recipe files:
- `/recipes/codebase_generator/generate_code.json`
- `/recipes/component_blueprint_generator/build_blueprint.json`
- `/recipes/recipe_executor/build_component.json`

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

## Code Integration

Recipe Executor integrates with Azure OpenAI through these key components:

1. **LLM Service (`llm.py`)**: Contains the `get_model` function which initializes the appropriate LLM model based on the provided identifier

2. **Azure Settings (`models.py`)**: Contains the `AzureOpenAISettings` Pydantic model for validating configuration

### Using Multiple Model Providers

While Azure OpenAI is now the default, Recipe Executor still supports other providers:

- OpenAI: `openai:model_name` (e.g., `openai:gpt-4o`)
- Anthropic: `anthropic:model_name` (e.g., `anthropic:claude-3-opus-20240229`)
- Gemini: `gemini:model_name` (e.g., `gemini:gemini-pro`)

## Deployment-Specific Considerations

### Azure OpenAI Resource Configuration

Ensure your Azure OpenAI resource has the appropriate model deployments:

1. Create deployments in Azure OpenAI Studio for each model you plan to use
2. Name your deployments consistently and use those names in your model identifiers
3. If using Managed Identity, ensure the identity has appropriate permissions on your Azure OpenAI resource

### Performance and Cost Management

When using Azure OpenAI:

1. **Token Optimization**: The system prompts and templates are designed to be efficient with token usage
2. **Deployment Selection**: Use smaller models like `o3-mini` for simpler tasks to reduce costs
3. **Rate Limiting**: Azure OpenAI has rate limits per deployment; consider these when running multiple concurrent recipes

## Troubleshooting

Common issues and solutions:

1. **Authentication Errors**:
   - Ensure your Azure OpenAI API key is correct
   - Check that Managed Identity has proper permissions if used

2. **Deployment Not Found**:
   - Verify the deployment name in your model identifier matches exactly with your Azure OpenAI deployment

3. **Endpoint Connection Issues**:
   - Ensure network connectivity to Azure OpenAI endpoints
   - Verify the correct endpoint URL format

4. **Model Response Format Errors**:
   - If you encounter parsing errors, it might be due to differences in response formats between models
   - Ensure system prompts are appropriate for the model deployment you're using

## Examples

### Basic Azure OpenAI Recipe

```json
{
  "steps": [
    {
      "type": "generate",
      "prompt": "Generate a simple Python function that calculates factorial.",
      "model": "azure:o3-mini:deployment-name",
      "artifact": "generated_code"
    },
    {
      "type": "write_file",
      "artifact": "generated_code",
      "root": "output"
    }
  ]
}
```

### Using Managed Identity Authentication

1. Set environment variable in `.env`:
   ```
   AZURE_USE_MANAGED_IDENTITY=true
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   ```

2. Run recipe with Azure OpenAI model:
   ```bash
   python recipe_executor/main.py path/to/recipe.json
   ```