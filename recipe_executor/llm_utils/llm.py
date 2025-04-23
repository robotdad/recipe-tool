import logging
import os
import time
from typing import List, Optional, Type, Union

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServer
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from recipe_executor.llm_utils.azure_openai import get_azure_openai_model

__all__ = ["LLM"]

# env var for default model
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai/gpt-4o")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def _get_model(logger: logging.Logger, model_id: Optional[str]) -> Union[OpenAIModel, AnthropicModel]:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider/model_name' or 'provider/model_name/deployment_name'.
    """
    if not model_id:
        model_id = DEFAULT_MODEL
    parts = model_id.split("/", 2)
    if len(parts) < 2:
        raise ValueError(f"Invalid model identifier '{model_id}', expected 'provider/model_name'")
    provider = parts[0].lower()
    model_name = parts[1]
    # azure may include a deployment name
    if provider == "azure":
        deployment_name: Optional[str] = parts[2] if len(parts) == 3 else None
        try:
            return get_azure_openai_model(
                logger=logger,
                model_name=model_name,
                deployment_name=deployment_name,
            )
        except Exception:
            logger.error(f"Failed to initialize Azure OpenAI model '{model_id}'", exc_info=True)
            raise
    if provider == "openai":
        # OpenAIModel will pick up OPENAI_API_KEY from env
        return OpenAIModel(model_name)
    if provider == "anthropic":
        return AnthropicModel(model_name)
    if provider == "ollama":
        # Ollama endpoint via OpenAIProvider
        base_url = OLLAMA_BASE_URL.rstrip("/") + "/v1"
        provider_client = OpenAIProvider(base_url=base_url)
        return OpenAIModel(model_name, provider=provider_client)
    raise ValueError(f"Unsupported LLM provider '{provider}' in model identifier '{model_id}'")


class LLM:
    """
    Unified interface for interacting with LLM providers and optional MCP servers.
    """

    def __init__(
        self,
        logger: logging.Logger,
        model: str = DEFAULT_MODEL,
        mcp_servers: Optional[List[MCPServer]] = None,
    ):
        self.logger: logging.Logger = logger
        self.model: str = model
        # store list or empty list
        self.mcp_servers: List[MCPServer] = mcp_servers if mcp_servers is not None else []

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        output_type: Type[Union[str, BaseModel]] = str,
        mcp_servers: Optional[List[MCPServer]] = None,
    ) -> Union[str, BaseModel]:
        """
        Generate an output from the LLM based on the provided prompt.
        """
        # Determine model identifier and servers
        model_id = model or self.model
        servers = mcp_servers if mcp_servers is not None else self.mcp_servers

        # Initialize model
        try:
            llm_model = _get_model(self.logger, model_id)
        except Exception:
            raise

        model_name = getattr(llm_model, "model_name", str(llm_model))

        # Create agent
        agent = Agent(
            model=llm_model,
            output_type=output_type,
            mcp_servers=servers or [],
        )
        # Logging before call
        self.logger.info(f"LLM request: model={model_name}")
        self.logger.debug(f"LLM request payload: prompt={prompt!r}, output_type={output_type}, mcp_servers={servers}")

        start_time = time.monotonic()
        try:
            # open MCP sessions if any
            async with agent.run_mcp_servers():
                result = await agent.run(prompt)
        except Exception:
            self.logger.error(f"LLM call failed for model {model_id}", exc_info=True)
            raise
        end_time = time.monotonic()

        # Logging after call
        duration = end_time - start_time
        usage = None
        try:
            usage = result.usage()
        except Exception:
            pass
        # debug full result
        self.logger.debug(f"LLM result payload: {result!r}")
        # info summary
        if usage:
            tokens = f"total={usage.total_tokens}, request={usage.request_tokens}, response={usage.response_tokens}"
        else:
            tokens = "unknown"
        self.logger.info(f"LLM completed in {duration:.2f}s, tokens used: {tokens}")

        # Return only the output
        return result.output
