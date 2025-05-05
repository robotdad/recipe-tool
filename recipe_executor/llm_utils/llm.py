import os
import time
import logging
from typing import Optional, List, Type, Union

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.mcp import MCPServer

from recipe_executor.llm_utils.azure_openai import get_azure_openai_model


def get_model(model_id: str, logger: logging.Logger) -> Union[OpenAIModel, AnthropicModel]:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider/model_name' or 'provider/model_name/deployment_name'.
    Supported providers: openai, azure, anthropic, ollama.
    """
    parts = model_id.split('/')
    if len(parts) < 2:
        raise ValueError(f"Invalid model_id format: '{model_id}'")
    provider = parts[0].lower()

    # OpenAI provider
    if provider == 'openai':
        if len(parts) != 2:
            raise ValueError(f"Invalid OpenAI model_id: '{model_id}'")
        model_name = parts[1]
        return OpenAIModel(model_name)

    # Azure OpenAI provider
    if provider == 'azure':
        if len(parts) == 2:
            model_name = parts[1]
            deployment_name = None
        elif len(parts) == 3:
            model_name = parts[1]
            deployment_name = parts[2]
        else:
            raise ValueError(f"Invalid Azure model_id: '{model_id}'")
        return get_azure_openai_model(
            logger=logger, model_name=model_name, deployment_name=deployment_name
        )

    # Anthropic provider
    if provider == 'anthropic':
        if len(parts) != 2:
            raise ValueError(f"Invalid Anthropic model_id: '{model_id}'")
        model_name = parts[1]
        return AnthropicModel(model_name)

    # Ollama provider (uses OpenAIModel with custom provider URL)
    if provider == 'ollama':
        if len(parts) != 2:
            raise ValueError(f"Invalid Ollama model_id: '{model_id}'")
        model_name = parts[1]
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        provider_obj = OpenAIProvider(base_url=f"{base_url}/v1")
        return OpenAIModel(model_name=model_name, provider=provider_obj)

    raise ValueError(f"Unsupported LLM provider: '{provider}' in model_id '{model_id}'")


class LLM:
    """
    Unified interface for interacting with various LLM providers
    and optional MCP servers.
    """
    def __init__(
        self,
        logger: logging.Logger,
        model: str = "openai/gpt-4o",
        max_tokens: Optional[int] = None,
        mcp_servers: Optional[List[MCPServer]] = None,
    ):
        self.logger: logging.Logger = logger
        self.default_model_id: str = model
        self.default_max_tokens: Optional[int] = max_tokens
        self.default_mcp_servers: List[MCPServer] = mcp_servers or []

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
        model_id = model or self.default_model_id
        tokens = max_tokens if max_tokens is not None else self.default_max_tokens
        servers = mcp_servers if mcp_servers is not None else self.default_mcp_servers

        # Info log: model selection
        try:
            provider = model_id.split('/', 1)[0]
        except Exception:
            provider = 'unknown'
        self.logger.info(
            "LLM generate using provider=%s model_id=%s", provider, model_id
        )

        # Debug log: request details
        output_name = getattr(output_type, '__name__', str(output_type))
        self.logger.debug(
            "LLM request payload prompt=%r model_id=%s max_tokens=%s output_type=%s",
            prompt, model_id, tokens, output_name
        )

        # Initialize model
        try:
            model_instance = get_model(model_id, self.logger)
        except ValueError as e:
            self.logger.error("Invalid model_id '%s': %s", model_id, str(e))
            raise

        # Prepare agent
        agent_kwargs = {
            'model': model_instance,
            'output_type': output_type,
            'mcp_servers': servers,
        }
        if tokens is not None:
            agent_kwargs['model_settings'] = ModelSettings(max_tokens=tokens)

        agent: Agent = Agent(**agent_kwargs)  # type: ignore

        # Execute request
        start_time = time.time()
        try:
            async with agent.run_mcp_servers():
                result = await agent.run(prompt)
        except Exception as e:
            self.logger.error(
                "LLM call failed for model_id=%s error=%s", model_id, str(e)
            )
            raise
        end_time = time.time()

        # Log result summary
        usage = None
        try:
            usage = result.usage()
        except Exception:
            usage = None
        duration = end_time - start_time
        if usage:
            self.logger.info(
                "LLM result time=%.3f sec requests=%d tokens_total=%d (req=%d res=%d)",
                duration,
                usage.requests,
                usage.total_tokens,
                usage.request_tokens,
                usage.response_tokens,
            )
        else:
            self.logger.info(
                "LLM result time=%.3f sec (usage unavailable)", duration
            )

        # Debug log: raw result
        self.logger.debug("LLM raw result: %r", result)

        return result.output
