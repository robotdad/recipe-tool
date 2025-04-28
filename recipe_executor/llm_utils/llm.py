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

# Default model identifier and Ollama endpoint
DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "openai/gpt-4o")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


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

    if provider == "azure":
        # Azure OpenAI may include a deployment name
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
        return OpenAIModel(model_name)

    if provider == "anthropic":
        return AnthropicModel(model_name)

    if provider == "ollama":
        base_url = OLLAMA_BASE_URL.rstrip("/") + "/v1"
        client = OpenAIProvider(base_url=base_url)
        return OpenAIModel(model_name, provider=client)

    raise ValueError(f"Unsupported LLM provider '{provider}' in model identifier '{model_id}'")


class LLM:
    """
    Unified interface for interacting with LLM providers and optional MCP servers.
    """

    def __init__(
        self,
        logger: logging.Logger,
        model: str = DEFAULT_MODEL,
        max_tokens: Optional[int] = None,
        mcp_servers: Optional[List[MCPServer]] = None,
    ):
        self.logger: logging.Logger = logger
        self.model: str = model
        self.max_tokens: Optional[int] = max_tokens
        self.mcp_servers: List[MCPServer] = mcp_servers if mcp_servers is not None else []

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        output_type: Type[Union[str, BaseModel]] = str,
        mcp_servers: Optional[List[MCPServer]] = None,
    ) -> Union[str, BaseModel]:
        """
        Generate an output from the LLM based on the provided prompt.
        """
        model_id = model or self.model
        servers = mcp_servers if mcp_servers is not None else self.mcp_servers
        tokens_limit = max_tokens if max_tokens is not None else self.max_tokens

        try:
            llm_model = _get_model(self.logger, model_id)
        except Exception:
            # Propagate initialization errors
            raise

        # Derive a human-readable model name for logging
        model_name = getattr(llm_model, "model_name", str(llm_model))

        agent = Agent(
            model=llm_model,
            output_type=output_type,
            mcp_servers=servers or [],
        )

        # Info-level: model invocation
        self.logger.info(f"LLM request: model={model_name}")
        # Debug-level: full request payload
        self.logger.debug(
            f"LLM request payload: prompt={prompt!r}, output_type={output_type},"
            f" max_tokens={tokens_limit}, mcp_servers={servers}"
        )

        start = time.monotonic()
        try:
            async with agent.run_mcp_servers():
                # Pass max_tokens if provided
                if tokens_limit is not None:
                    result = await agent.run(prompt, model_settings={"max_tokens": tokens_limit})
                else:
                    result = await agent.run(prompt)
        except Exception:
            self.logger.error(f"LLM call failed for model '{model_id}'", exc_info=True)
            raise
        end = time.monotonic()

        duration = end - start
        usage_info = None
        try:
            usage = result.usage()
            usage_info = (usage.total_tokens, usage.request_tokens, usage.response_tokens)
        except Exception:
            pass

        # Debug-level: full result payload
        self.logger.debug(f"LLM result payload: {result!r}")

        # Info-level: summary of execution
        if usage_info:
            total, req, resp = usage_info
            tokens_str = f"total={total}, request={req}, response={resp}"
        else:
            tokens_str = "unknown"
        self.logger.info(f"LLM completed in {duration:.2f}s, tokens used: {tokens_str}")

        return result.output
