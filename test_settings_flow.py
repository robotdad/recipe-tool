#!/usr/bin/env python3
"""Test script to verify settings flow from sidebar to LLM generation."""

import os
import asyncio
from recipe_executor.context import Context
from recipe_executor.config import load_configuration
from recipe_executor.llm_utils.llm import get_model

async def test_settings_flow():
    """Test that settings properly flow through the system."""
    
    # Set some test environment variables
    os.environ["OPENAI_API_KEY"] = "test-key-123"
    os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"
    os.environ["AZURE_OPENAI_BASE_URL"] = "https://test.openai.azure.com/"
    
    # Load configuration as the apps do
    config = load_configuration()
    print("Loaded config:")
    for key, value in config.items():
        if "key" in key.lower():
            print(f"  {key}: ***hidden***")
        else:
            print(f"  {key}: {value}")
    
    # Create context with artifacts and config
    artifacts = {
        "model": "openai/gpt-4o",
        "max_tokens": "1000",
    }
    context = Context(artifacts=artifacts, config=config)
    
    # Verify config is accessible
    ctx_config = context.get_config()
    print("\nContext config:")
    for key, value in ctx_config.items():
        if "key" in key.lower():
            print(f"  {key}: ***hidden***")
        else:
            print(f"  {key}: {value}")
    
    # Test get_model function
    model_id = artifacts["model"]
    try:
        model = get_model(model_id, context)
        print(f"\nSuccessfully created model for: {model_id}")
        print(f"Model type: {type(model).__name__}")
    except Exception as e:
        print(f"\nError creating model: {e}")
    
    # Test with Azure
    azure_model_id = "azure/gpt-4o/test-deployment"
    artifacts["model"] = azure_model_id
    context2 = Context(artifacts=artifacts, config=config)
    try:
        model2 = get_model(azure_model_id, context2)
        print(f"\nSuccessfully created Azure model for: {azure_model_id}")
        print(f"Model type: {type(model2).__name__}")
    except Exception as e:
        print(f"\nError creating Azure model: {e}")

if __name__ == "__main__":
    asyncio.run(test_settings_flow())