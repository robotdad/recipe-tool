# recipe_executor/llm.py

import logging

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
            "Do not output any extra text."
        ),
        result_type=FileGenerationResult,
    )
except Exception as e:
    logger.error("Failed to initialize LLM agent: %s", e)
    agent = None


def call_llm(prompt: str) -> FileGenerationResult:
    """
    Calls the LLM via Pydantic-AI and returns a structured FileGenerationResult.
    If the agent isn't initialized or the call fails, returns a dummy FileGenerationResult.
    """
    if agent is not None:
        try:
            result: AgentRunResult[FileGenerationResult] = agent.run_sync(prompt)
            return result.data
        except Exception as e:
            logger.error("LLM call failed: %s", e, exc_info=True)
            raise e
    else:
        # Dummy fallback for testing purposes.
        dummy_file = FileSpec(path="generated/hello.py", content='print("Hello, Test!")')
        return FileGenerationResult(files=[dummy_file], commentary="Dummy LLM output")
