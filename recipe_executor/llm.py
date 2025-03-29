# recipe_executor/llm.py

import logging
import time

from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult

from recipe_executor.models import FileGenerationResult, FileSpec

logger = logging.getLogger("RecipeExecutor")

try:
    agent = Agent(
        model="openai:gpt-4",
        system_prompt=(
            "You are a code generation assistant. Given a specification, "
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
except Exception as e:
    logger.error("Failed to initialize LLM agent: %s", e)
    agent = None


def call_llm(prompt: str) -> FileGenerationResult:
    """
    Calls the LLM via Pydantic-AI and returns a structured FileGenerationResult.

    Always logs the LLM request prompt and the full response at the debug level,
    along with the time taken for the call. If the agent isn't initialized or the call fails,
    returns a dummy FileGenerationResult.
    """
    logger.debug("LLM request prompt: %s", prompt)

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
