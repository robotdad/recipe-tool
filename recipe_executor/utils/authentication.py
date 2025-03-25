"""Authentication utilities for the Recipe Executor."""

import os
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Tuple


class Provider(str, Enum):
    """Supported model providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    MISTRAL = "mistral"
    GROQ = "groq"
    OLLAMA = "ollama"  # Local model, no API key needed


class AuthManager:
    """Manages authentication for different model providers."""

    def __init__(self):
        """Initialize the authentication manager."""
        # Map of provider to environment variable name
        self.provider_env_vars = {
            Provider.ANTHROPIC: "ANTHROPIC_API_KEY",
            Provider.OPENAI: "OPENAI_API_KEY",
            Provider.GOOGLE: "GOOGLE_API_KEY",
            Provider.MISTRAL: "MISTRAL_API_KEY",
            Provider.GROQ: "GROQ_API_KEY",
        }

        # Provider-specific documentation URLs
        self.provider_docs = {
            Provider.ANTHROPIC: "https://anthropic.com/keys",
            Provider.OPENAI: "https://platform.openai.com/api-keys",
            Provider.GOOGLE: "https://aistudio.google.com/app/apikey",
            Provider.MISTRAL: "https://console.mistral.ai/api-keys",
            Provider.GROQ: "https://console.groq.com/keys",
        }

    def verify_api_key(self, provider: str) -> Tuple[bool, Optional[str]]:
        """Verify if the required API key is available for this provider.

        Args:
            provider: The provider to check for an API key

        Returns:
            A tuple of (is_valid, error_message)
        """
        # Normalize the provider
        try:
            provider_enum = Provider(provider.lower())
        except ValueError:
            return False, f"Unknown provider: {provider}. Supported providers are: {', '.join([p.value for p in Provider])}"

        # Ollama is a special case - no API key needed
        if provider_enum == Provider.OLLAMA:
            return True, None

        # Get the environment variable name for this provider
        env_var = self.provider_env_vars.get(provider_enum)
        if not env_var:
            return False, f"No API key environment variable defined for provider: {provider}"

        # Check if the API key exists
        api_key = os.environ.get(env_var)
        if not api_key:
            docs_url = self.provider_docs.get(provider_enum, "")
            return (
                False,
                f"Missing API key for {provider_enum.value.title()}. The {env_var} environment variable is not set."
                f"\nYou can obtain an API key from: {docs_url}",
            )

        # Basic validation of API key format
        if len(api_key.strip()) < 8:
            return False, f"API key for {provider_enum.value.title()} appears to be invalid (too short)"

        return True, None

    def verify_recipe_providers(self, providers: list) -> Dict[str, str]:
        """Verify all providers needed by a recipe.

        Args:
            providers: List of provider names to verify

        Returns:
            Dictionary of provider names to error messages for any invalid providers
        """
        invalid_providers = {}
        for provider in providers:
            is_valid, error_message = self.verify_api_key(provider)
            if not is_valid:
                invalid_providers[provider] = error_message
        return invalid_providers

    def get_api_key_instructions(self, provider: str) -> str:
        """Get instructions for setting up an API key for a provider.

        Args:
            provider: The provider name

        Returns:
            Instructions string
        """
        try:
            provider_enum = Provider(provider.lower())
        except ValueError:
            return f"Unknown provider: {provider}"

        if provider_enum == Provider.OLLAMA:
            return "Ollama is a local provider and does not require an API key."

        env_var = self.provider_env_vars.get(provider_enum)
        docs_url = self.provider_docs.get(provider_enum, "")

        instructions = f"\nTo setup {provider_enum.value.title()} API key:\n"
        instructions += f"1. Create a .env file in the project root directory with the following content:\n"
        instructions += f"   {env_var}=your-api-key-here\n"
        instructions += f"2. Or export the key in your shell environment before running the command:\n"
        instructions += f"   export {env_var}=your-api-key-here\n"
        if docs_url:
            instructions += f"\nYou can obtain an API key from: {docs_url}\n"

        return instructions
