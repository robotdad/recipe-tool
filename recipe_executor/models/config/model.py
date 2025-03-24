"""Model configuration for LLM models."""

from typing import Literal, Optional

from pydantic import BaseModel


class ModelConfig(BaseModel):
    """Configuration for an LLM model."""

    provider: Literal["anthropic", "openai", "google", "mistral", "ollama", "groq"] = (
        "anthropic"
    )
    model_name: str = "claude-3-7-sonnet-20250219"
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None
