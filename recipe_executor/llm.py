# recipe_executor/llm.py

import logging
import time
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.models import Model
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel

from recipe_executor.models import FileGenerationResult, FileSpec

logger = logging.getLogger("RecipeExecutor")


def get_model(model_id: str) -> Model:
    """
    Initializes the LLM model based on the provided model_id.
    The model_id should be in the format 'provider:model_name'.
    Supported providers are 'anthropic', 'gemini', and 'openai'.
    """

    try:
        provider, model_name = model_id.split(":")
    except ValueError:
        logger.error("Invalid model_id format. Expected 'provider:model_name'.")
        raise ValueError("Invalid model_id format. Expected 'provider:model_name'.")

    match provider:
        case "anthropic":
            return AnthropicModel(model_name=model_name)
        case "gemini":
            return GeminiModel(model_name=model_name)
        case "openai":
            return OpenAIModel(model_name=model_name)
        case _:
            raise ValueError(
                "Unknown provider '%s'. Supported providers are 'anthropic', 'gemini', and 'openai'.", provider
            )


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initializes the LLM agent with the specified model name.

    If no model name is provided, defaults to "o3-mini". The agent is configured
    with a system prompt that instructs it to generate a JSON object with
    specific keys and formatting requirements. The agent is set to retry
    requests up to 3 times in case of failures.
    """

    if model_id is None:
        model_id = "openai:gpt-4o"

    model = get_model(model_id)
    logger.debug("Initializing LLM agent with model: %s", model.model_name)

    try:
        agent = Agent(
            model=model,
            system_prompt=(
                "You are a file generation assistant. Given a specification, "
                "generate a JSON object with exactly two keys: 'files' and 'commentary'. "
                "The 'files' key should be a list of file objects with 'path' and 'content'. "
                "IMPORTANT: When including code with backslashes (like Windows paths or regex), "
                "ensure they are properly escaped for JSON (use \\\\ instead of \\). "
                "All special characters in string values must be properly JSON-escaped. "
                "Do not output any extra text."
            ),
            retries=3,
            result_type=FileGenerationResult,
        )
        logger.debug("LLM agent initialized successfully.")
        return agent
    except Exception as e:
        logger.error("Failed to initialize LLM agent: %s", e)
        raise e


def call_llm(prompt: str, model: Optional[str] = None) -> FileGenerationResult:
    """
    Calls the LLM via Pydantic-AI and returns a structured FileGenerationResult.

    Always logs the LLM request prompt and the full response at the debug level,
    along with the time taken for the call. If the agent isn't initialized or the call fails,
    returns a dummy FileGenerationResult.
    """
    logger.debug("LLM request prompt: %s", prompt)

    agent = get_agent(model_id=model)

    if agent is not None:
        try:
            start_time = time.perf_counter()
            result: AgentRunResult[FileGenerationResult] = agent.run_sync(prompt)
            elapsed_time = time.perf_counter() - start_time

            logger.debug("LLM response received in %.2f seconds: %s", elapsed_time, result.data)

            return result.data
        except Exception as e:
            logger.error("LLM call failed: %s", e, exc_info=True)
            raise e
    else:
        # Dummy fallback for testing purposes.
        dummy_file = FileSpec(path="generated/hello.py", content='print("Hello, Test!")')
        return FileGenerationResult(files=[dummy_file], commentary="Dummy LLM output")
