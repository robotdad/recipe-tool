Scanning patterns: ['recipe_executor']
Excluding patterns: ['.venv', 'node_modules', '.git', '__pycache__', '*.pyc']
Including patterns: []
Found 14 files.

=== File: recipe_executor/context.py ===
from dataclasses import dataclass, field
from typing import Any, Iterator


@dataclass
class Context:
    """Holds artifacts and optional config, providing dict-like access to artifacts."""

    artifacts: dict = field(default_factory=dict)
    config: dict = field(default_factory=dict)  # for any global settings or legacy compat

    def __init__(self, artifacts=None, config=None) -> None:
        # Only keep artifacts and config in context
        self.artifacts = artifacts or {}
        self.config = config or {}

    def __getitem__(self, key) -> Any:
        # Enable dict-like read access to artifacts
        return self.artifacts[key]

    def __setitem__(self, key, value) -> None:
        # Enable dict-like write access to artifacts
        self.artifacts[key] = value

    def get(self, key, default=None) -> Any:
        # Safe get method for artifacts
        return self.artifacts.get(key, default)

    def as_dict(self) -> dict[Any, Any]:
        """Return a shallow copy of artifact data (for templating)."""
        return dict(self.artifacts)

    def __iter__(self) -> Iterator[Any]:
        # Iterate over artifact keys (to support dict-like behavior)
        return iter(self.artifacts)

    def __len__(self) -> int:
        # Number of artifacts stored
        return len(self.artifacts)

    def keys(self):
        # Keys of the artifacts dictionary
        return self.artifacts.keys()



=== File: recipe_executor/executor.py ===
import json
import logging
import os
import re
from typing import Optional

from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY


class RecipeExecutor:
    """
    Unified executor that loads a recipe (from a file path, JSON string, or dict),
    and executes its steps sequentially using the provided context.
    """

    def execute(self, recipe, context: Context, logger: Optional[logging.Logger] = None) -> None:
        logger = logger or logging.getLogger("RecipeExecutor")

        # Load recipe data from different input types.
        if isinstance(recipe, str):
            if os.path.isfile(recipe):
                with open(recipe, "r", encoding="utf-8") as f:
                    content = f.read()

                # Try to extract JSON from a fenced code block (```json ... ```)
                match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
                if match:
                    snippet = match.group(1).strip()
                    if not snippet:
                        raise ValueError("The JSON code block in the recipe file is empty.")
                    try:
                        recipe_data = json.loads(snippet)
                    except Exception as e:
                        logger.error("Failed to parse JSON from the code block.", exc_info=True)
                        raise e
                else:
                    # Fallback: try to parse the entire file as JSON
                    content_stripped = content.strip()
                    if not content_stripped:
                        raise ValueError("Recipe file is empty.")
                    try:
                        recipe_data = json.loads(content_stripped)
                    except Exception as e:
                        logger.error("Failed to parse the entire recipe file as JSON.", exc_info=True)
                        raise e
            else:
                # If the string is not a file path, treat it as a JSON string.
                try:
                    recipe_data = json.loads(recipe)
                except Exception as e:
                    logger.error("Failed to parse the recipe string as JSON.", exc_info=True)
                    raise e
        elif isinstance(recipe, dict):
            recipe_data = recipe
        else:
            raise TypeError("Recipe must be a file path, JSON string, or a dictionary.")

        # Extract steps: if recipe_data is a dict with a 'steps' key, use it; otherwise, assume it's a list.
        if isinstance(recipe_data, dict) and "steps" in recipe_data:
            steps = recipe_data["steps"]
        elif isinstance(recipe_data, list):
            steps = recipe_data
        else:
            raise ValueError("Recipe data must be a list of steps or a dict with a 'steps' key.")

        logger.info(f"Loaded recipe with {len(steps)} steps.")

        # Execute each step sequentially.
        for idx, step_def in enumerate(steps):
            if not isinstance(step_def, dict):
                raise ValueError(f"Step {idx + 1} is not a valid dictionary.")

            step_type = step_def.get("type")
            if not step_type:
                raise ValueError(f"Step {idx + 1} is missing the 'type' field.")

            step_cls = STEP_REGISTRY.get(step_type)
            if step_cls is None:
                raise ValueError(f"Unknown step type '{step_type}' in step {idx + 1}.")

            logger.info(f"Executing step {idx + 1}: {step_type}")
            try:
                # Instantiate and execute the step.
                step_instance = step_cls(config=step_def, logger=logger)
                step_instance.execute(context)
                logger.info(f"Completed step {idx + 1}: {step_type}")
            except Exception as e:
                logger.error(f"Error executing step {idx + 1} ({step_type}): {e}", exc_info=True)
                raise e



=== File: recipe_executor/llm.py ===
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



=== File: recipe_executor/logger.py ===
import logging
import os
import sys


def init_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files.

    Returns:
        logging.Logger: Configured logger instance.
    """
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger("RecipeExecutor")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # Clear old handlers to avoid duplicates (useful during dev reloads)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Stream handler for stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # File handlers
    def add_file_handler(filename: str, level: int):
        path = os.path.join(log_dir, filename)
        with open(path, "w"):  # truncate file
            pass
        handler = logging.FileHandler(path)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    add_file_handler("debug.log", logging.DEBUG)
    add_file_handler("info.log", logging.INFO)
    add_file_handler("error.log", logging.ERROR)

    return logger



=== File: recipe_executor/main.py ===
#!/usr/bin/env python3
import argparse

from context import Context
from executor import RecipeExecutor

from recipe_executor.logger import init_logger


def main() -> None:
    """
    CLI entry point for the Recipe Executor Tool.

    Parses command-line arguments and calls the core runner function.
    """
    parser = argparse.ArgumentParser(
        description="Recipe Executor Tool - Generates code based on a recipe using context for path values."
    )
    parser.add_argument("recipe_path", help="Path to the recipe markdown file")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files (default: logs)")
    parser.add_argument("--context", action="append", help="Additional context values as key=value pairs")
    args = parser.parse_args()

    # Convert CLI --context values (key=value) to a dictionary
    cli_context = {}
    if args.context:
        for item in args.context:
            if "=" in item:
                key, value = item.split("=", 1)
                cli_context[key.strip()] = value.strip()

    logger = init_logger(args.log_dir)
    logger.info("Starting Recipe Executor Tool")

    # Inject CLI context values into Context.artifacts
    context = Context(artifacts=cli_context)

    executor = RecipeExecutor()
    executor.execute(args.recipe_path, context, logger=logger)


if __name__ == "__main__":
    main()



=== File: recipe_executor/models.py ===
from typing import List, Optional

from pydantic import BaseModel


class ReadFileConfig(BaseModel):
    file_path: str
    store_key: str = "spec"  # Key under which to store the file content


class GenerateCodeConfig(BaseModel):
    input_key: str = "spec"  # Key in context where the specification is stored
    output_key: str = "codegen_result"  # Key to store the generated code result


class WriteFileConfig(BaseModel):
    input_key: str = "codegen_result"  # Key in context where the codegen result is stored
    output_root: str  # Root directory where files will be written


class FileSpec(BaseModel):
    path: str
    content: str


class FileGenerationResult(BaseModel):
    files: List[FileSpec]
    commentary: Optional[str] = None


class RecipeStep(BaseModel):
    type: str
    config: dict


class Recipe(BaseModel):
    steps: List[RecipeStep]



=== File: recipe_executor/steps/__init__.py ===
# __init__.py

from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.generate_llm import GenerateWithLLMStep
from recipe_executor.steps.read_file import ReadFileStep
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.write_files import WriteFileStep

# Explicitly populate the registry
STEP_REGISTRY.update({
    "read_file": ReadFileStep,
    "write_file": WriteFileStep,
    "generate": GenerateWithLLMStep,
    "execute_recipe": ExecuteRecipeStep,
})



=== File: recipe_executor/steps/base.py ===
import logging
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

from recipe_executor.context import Context


class StepConfig(BaseModel):
    """Base class for all step configs. Extend this in each step."""

    pass


ConfigType = TypeVar("ConfigType", bound=StepConfig)


class BaseStep(Generic[ConfigType]):
    """
    Base class for all steps. Subclasses must implement `execute(context)`.
    Each step receives a config object and a logger.
    """

    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config: ConfigType = config
        self.logger = logger or logging.getLogger("RecipeExecutor")

    def execute(self, context: Context) -> None:
        raise NotImplementedError("Each step must implement the `execute()` method.")



=== File: recipe_executor/steps/execute_recipe.py ===
import os

from recipe_executor.context import Context
from recipe_executor.executor import RecipeExecutor
from recipe_executor.steps.base import BaseStep, StepConfig


class ExecuteRecipeConfig(StepConfig):
    """Config for ExecuteRecipeStep."""

    recipe_path: str


class ExecuteRecipeStep(BaseStep):
    """
    Step that executes a sub-recipe using the same context.
    """

    def __init__(self, config: dict, logger=None) -> None:
        super().__init__(ExecuteRecipeConfig(**config), logger)

    def execute(self, context: Context) -> None:
        recipe_path = self.config.recipe_path

        if not os.path.exists(recipe_path):
            raise FileNotFoundError(f"Sub-recipe file not found: {recipe_path}")

        self.logger.info(f"Executing sub-recipe: {recipe_path}")

        executor = RecipeExecutor()
        executor.execute(recipe=recipe_path, context=context, logger=self.logger)

        self.logger.info(f"Completed sub-recipe: {recipe_path}")



=== File: recipe_executor/steps/generate_llm.py ===
from recipe_executor.context import Context
from recipe_executor.llm import call_llm
from recipe_executor.steps.base import BaseStep, StepConfig


class GenerateLLMConfig(StepConfig):
    """
    Config for GenerateWithLLMStep.

    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        artifact: The name under which to store the LLM response in context.
    """

    prompt: str
    artifact: str


class GenerateWithLLMStep(BaseStep[GenerateLLMConfig]):
    """
    Step that calls an LLM with a prompt and stores the result as a context artifact.
    """

    def __init__(self, config: dict, logger=None) -> None:
        super().__init__(GenerateLLMConfig(**config), logger)

    def execute(self, context: Context) -> None:
        self.logger.info(f"Calling LLM with prompt for artifact: {self.config.artifact}")
        response = call_llm(self.config.prompt)
        context[self.config.artifact] = response
        self.logger.debug(f"LLM response stored in context under '{self.config.artifact}'")



=== File: recipe_executor/steps/read_file.py ===
import os

from recipe_executor.context import Context
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class ReadFileConfig(StepConfig):
    """
    Config for ReadFileStep.

    Fields:
        path: Path to the file to read (may be templated).
        artifact: Name to store the file contents in context.
    """

    path: str
    artifact: str


class ReadFileStep(BaseStep[ReadFileConfig]):
    """
    Step that reads a file and stores its contents in the context under the specified key.
    """

    def __init__(self, config: dict, logger=None):
        super().__init__(ReadFileConfig(**config), logger)

    def execute(self, context: Context) -> None:
        path = render_template(self.config.path, context)

        if not os.path.exists(path):
            raise FileNotFoundError(f"ReadFileStep: file not found at path: {path}")

        self.logger.info(f"Reading file from: {path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        context[self.config.artifact] = content
        self.logger.debug(f"Stored file contents in context under key: '{self.config.artifact}'")



=== File: recipe_executor/steps/registry.py ===
# registry.py

# This is the shared registry for all steps.
STEP_REGISTRY = {}



=== File: recipe_executor/steps/write_files.py ===
import os

from recipe_executor.context import Context
from recipe_executor.models import FileGenerationResult, FileSpec
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFileStep.

    Fields:
        artifact: Name of the context key holding a CodeGenResult or List[FileSpec].
        root: Optional base path to prepend to all output file paths.
    """

    artifact: str
    root: str = "."


class WriteFileStep(BaseStep[WriteFilesConfig]):
    """
    Step that writes one or more files from context to disk.
    Accepts either a CodeGenResult or list of FileSpec dicts.
    """

    def __init__(self, config: dict, logger=None):
        super().__init__(WriteFilesConfig(**config), logger)

    def execute(self, context: Context) -> None:
        data = context.get(self.config.artifact)

        if data is None:
            raise ValueError(f"WriteFileStep: no artifact found at key: {self.config.artifact}")

        if isinstance(data, FileGenerationResult):
            files = data.files
        elif isinstance(data, list) and all(isinstance(f, FileSpec) for f in data):
            files = data
        else:
            raise TypeError("WriteFileStep: expected FileGenerationResult or list of FileSpec objects")

        output_root = render_template(self.config.root, context)

        for file in files:
            rel_path = render_template(file.path, context)
            full_path = os.path.join(output_root, rel_path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(file.content)

            self.logger.info(f"Wrote file: {full_path}")



=== File: recipe_executor/utils.py ===
from context import Context
from liquid import Template


def render_template(text: str, context: Context) -> str:
    """
    Render the given text as a Liquid template using the provided context.

    If the context object has an 'as_dict' method, it will be used to convert
    the context to a plain dictionary.

    Args:
        text (str): The template text to render.
        context (Dict[str, Any]): The context for rendering the template.

    Returns:
        str: The rendered text.
    """

    template = Template(text)
    return template.render(**context.as_dict())



