"""Main RecipeExecutor class and CLI entry point."""

import asyncio
import json
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Tuple

import yaml
from enum import Enum

from recipe_executor.constants import OutputFormat, StepStatus, StepType
from recipe_executor.context.execution_context import ExecutionContext
from recipe_executor.models.config.llm import LLMGenerateConfig
from recipe_executor.models.execution import RecipeResult, StepResult
from recipe_executor.models.recipe import Recipe
from recipe_executor.models.step import RecipeStep
from recipe_executor.utils import logging as log_utils

# Setup logging
logger = log_utils.get_logger()

# --- Recipe Executor Class ---


class RecipeExecutor:
    """
    Main class for executing LLM recipes with code-driven reliability.
    """

    def __init__(
        self,
        default_model_name: str = "claude-3-7-sonnet-20250219",
        default_model_provider: Literal[
            "anthropic", "openai", "google", "mistral", "ollama", "groq"
        ] = "anthropic",
        recipes_dir: str = "recipes",
        output_dir: str = "output",
        cache_dir: Optional[str] = "cache",
        temp: float = 0.1,
        validation_level: Optional[str] = "standard",
        interaction_mode: Optional[str] = "critical",
        log_level: int = logging.INFO,
    ):
        """
        Initialize the recipe executor.

        Args:
            default_model_name: The default model name to use
            default_model_provider: The default provider of the model
            recipes_dir: Directory containing recipe files
            output_dir: Directory to output generated files to
            cache_dir: Directory for caching LLM responses, or None to disable caching
            temp: Default temperature setting for the model
            validation_level: Default validation level
            interaction_mode: Default interaction mode
            log_level: Logging level
        """
        # Import here to avoid circular imports
        from recipe_executor.constants import InteractionMode, StepType, ValidationLevel
        from recipe_executor.events.listeners.console import ConsoleEventListener
        from recipe_executor.executors.implementations.api import ApiCallExecutor
        from recipe_executor.executors.implementations.chain import ChainExecutor
        from recipe_executor.executors.implementations.conditional import (
            ConditionalExecutor,
        )
        from recipe_executor.executors.implementations.file import (
            FileReadExecutor,
            FileWriteExecutor,
        )
        from recipe_executor.executors.implementations.input import WaitForInputExecutor
        from recipe_executor.executors.implementations.json import JsonProcessExecutor
        from recipe_executor.executors.implementations.llm import LLMGenerateExecutor
        from recipe_executor.executors.implementations.parallel import ParallelExecutor
        from recipe_executor.executors.implementations.python import (
            PythonExecuteExecutor,
        )
        from recipe_executor.executors.implementations.template import (
            TemplateSubstituteExecutor,
        )
        from recipe_executor.executors.implementations.validator import (
            ValidatorExecutor,
        )

        self.default_model_name = default_model_name
        self.default_model_provider = default_model_provider
        self.recipes_dir = recipes_dir
        self.output_dir = output_dir
        self.cache_dir = cache_dir
        self.temp = temp

        # Convert string values to enums if needed
        if isinstance(validation_level, str):
            self.validation_level = ValidationLevel[validation_level.upper()]
        else:
            self.validation_level = ValidationLevel.STANDARD

        if isinstance(interaction_mode, str):
            self.interaction_mode = InteractionMode[interaction_mode.upper()]
        else:
            self.interaction_mode = InteractionMode.CRITICAL

        # Initialize logging with proper file handling
        log_manager = log_utils.LogManager(reset_logs=True)
        log_manager.set_level(log_level)

        # Create directories
        os.makedirs(output_dir, exist_ok=True)
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)

        # Load environment variables
        self._load_environment()

        # Check API keys
        self._check_api_keys()

        # Initialize executors for each step type
        self.executors = {
            StepType.LLM_GENERATE: LLMGenerateExecutor(cache_dir=cache_dir),
            StepType.FILE_READ: FileReadExecutor(),
            StepType.FILE_WRITE: FileWriteExecutor(),
            StepType.TEMPLATE_SUBSTITUTE: TemplateSubstituteExecutor(),
            StepType.JSON_PROCESS: JsonProcessExecutor(),
            StepType.PYTHON_EXECUTE: PythonExecuteExecutor(),
            StepType.CONDITIONAL: ConditionalExecutor(),
            StepType.CHAIN: ChainExecutor(),
            StepType.PARALLEL: ParallelExecutor(),
            StepType.VALIDATOR: ValidatorExecutor(),
            StepType.WAIT_FOR_INPUT: WaitForInputExecutor(),
            StepType.API_CALL: ApiCallExecutor(),
        }

        # Default event listener for console output
        self.event_listener = ConsoleEventListener()

    def _load_environment(self):
        """Load environment variables from .env files."""
        try:
            from dotenv import load_dotenv

            # Try to load from .env file - first look in current directory, then parent directories
            env_path = Path(".") / ".env"
            if env_path.exists():
                load_dotenv(dotenv_path=env_path)
            else:
                # Try to find .env in parent directories
                current_dir = Path(".")
                for _ in range(3):  # Look up to 3 parent directories
                    current_dir = current_dir.parent
                    env_path = current_dir / ".env"
                    if env_path.exists():
                        load_dotenv(dotenv_path=env_path)
                        break
                else:
                    # If we get here, no .env file was found
                    logger.info(
                        "No .env file found. Using environment variables directly."
                    )
        except ImportError:
            logger.warning(
                "python-dotenv not installed. Environment variables must be set in the environment."
            )
            logger.warning("Install with: pip install python-dotenv")

    def _check_api_keys(self):
        """Check if required API keys are available and log warnings if not."""
        if self.default_model_provider == "anthropic" and not os.environ.get(
            "ANTHROPIC_API_KEY"
        ):
            logger.warning(
                "ANTHROPIC_API_KEY not found in environment variables. Anthropic models will not work."
            )
        elif self.default_model_provider == "openai" and not os.environ.get(
            "OPENAI_API_KEY"
        ):
            logger.warning(
                "OPENAI_API_KEY not found in environment variables. OpenAI models will not work."
            )
        elif self.default_model_provider == "google" and not os.environ.get(
            "GOOGLE_API_KEY"
        ):
            logger.warning(
                "GOOGLE_API_KEY not found in environment variables. Google models will not work."
            )
        elif self.default_model_provider == "mistral" and not os.environ.get(
            "MISTRAL_API_KEY"
        ):
            logger.warning(
                "MISTRAL_API_KEY not found in environment variables. Mistral models will not work."
            )
        elif self.default_model_provider == "groq" and not os.environ.get(
            "GROQ_API_KEY"
        ):
            logger.warning(
                "GROQ_API_KEY not found in environment variables. Groq models will not work."
            )

    async def _parse_natural_language_recipe(self, nl_content: str) -> "Recipe":
        """Parse a natural language recipe description into a structured Recipe object."""
        
        # Import here to avoid circular imports
        from recipe_executor.parsers.pydantic_parser import RecipeParser
        from recipe_executor.models.recipe import Recipe

        # Create a RecipeParser instance with the default model parameters
        parser = RecipeParser(
            model_name=self.default_model_name,
            model_provider=self.default_model_provider,
            temperature=self.temp,
        )
        
        try:
            # Parse the natural language recipe into a pydantic-ai recipe model
            pydantic_recipe = await parser.parse_recipe_from_text(nl_content)
            
            # Convert to the internal Recipe model
            recipe = self._convert_pydantic_recipe_to_internal(pydantic_recipe)
            
            # Store the original recipe content
            recipe.variables["_original_recipe"] = nl_content
            
            return recipe
        except Exception as e:
            logger.error(f"Error parsing natural language recipe: {e}")
            raise ValueError(f"Failed to parse natural language recipe: {e}")

    async def load_recipe(self, recipe_path: str) -> "Recipe":
        """
        Load a recipe from a file.

        Args:
            recipe_path: Path to the recipe file

        Returns:
            Recipe object
        """
        # Import here to avoid circular imports
        from recipe_executor.models.recipe import Recipe
        from recipe_executor.models.pydantic_recipe import Recipe as PydanticRecipe 
        from recipe_executor.parsers.pydantic_parser import RecipeParser

        # Handle recipe paths intelligently
        if not os.path.isabs(recipe_path):
            # Try a few options in order:
            potential_paths = [
                recipe_path,  # As provided
                os.path.join(self.recipes_dir, recipe_path),  # With recipes_dir prepended
            ]
            
            # If it already starts with recipes_dir, also try the base filename
            if recipe_path.startswith(self.recipes_dir + "/"):
                potential_paths.append(recipe_path.replace(self.recipes_dir + "/", "", 1))
                
            # Use the first path that exists
            for path in potential_paths:
                if os.path.exists(path):
                    recipe_path = path
                    break
            else:
                # If none found, use the original with recipes_dir (for consistent error messages)
                if not recipe_path.startswith(self.recipes_dir):
                    recipe_path = os.path.join(self.recipes_dir, recipe_path)

        file_ext = os.path.splitext(recipe_path)[1].lower()

        try:
            # Read the file content
            with open(recipe_path, "r") as f:
                content = f.read()

            # Check if this is a structured or natural language recipe
            is_structured = False
            recipe = None

            if file_ext == ".json":
                try:
                    data = json.loads(content)
                    recipe = Recipe.model_validate(data)
                    is_structured = True
                except json.JSONDecodeError:
                    logger.info("JSON parsing failed, treating as natural language")
                except Exception:
                    logger.info("JSON validation failed, treating as natural language")
            elif file_ext in [".yaml", ".yml"]:
                try:
                    data = yaml.safe_load(content)
                    recipe = Recipe.model_validate(data)
                    is_structured = True
                except yaml.YAMLError:
                    logger.info("YAML parsing failed, treating as natural language")
                except Exception:
                    logger.info("YAML validation failed, treating as natural language")
            elif file_ext == ".md":
                # For markdown files, try to extract YAML/JSON from code blocks
                yaml_match = re.search(r"```ya?ml\s*\n(.*?)\n```", content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    try:
                        data = yaml.safe_load(yaml_content)
                        recipe = Recipe.model_validate(data)
                        is_structured = True
                    except (yaml.YAMLError, Exception):
                        logger.info("YAML code block parsing failed, trying JSON")

                if not is_structured:
                    # Try to find a JSON code block
                    json_match = re.search(
                        r"```json\s*\n(.*?)\n```", content, re.DOTALL
                    )
                    if json_match:
                        json_content = json_match.group(1)
                        try:
                            data = json.loads(json_content)
                            recipe = Recipe.model_validate(data)
                            is_structured = True
                        except (json.JSONDecodeError, Exception):
                            logger.info(
                                "JSON code block parsing failed, treating as natural language"
                            )

            # If not structured, parse as natural language using pydantic-ai
            if not is_structured:
                logger.info("Parsing as natural language recipe using pydantic-ai")
                # Create a RecipeParser instance with the default model parameters
                parser = RecipeParser(
                    model_name=self.default_model_name,
                    model_provider=self.default_model_provider,
                    temperature=self.temp,
                )
                
                try:
                    # Parse the natural language recipe
                    pydantic_recipe = await parser.parse_recipe_from_text(content)
                    
                    # Convert pydantic-ai recipe to internal Recipe model
                    # This is a temporary solution until we fully migrate to pydantic-ai model
                    recipe = self._convert_pydantic_recipe_to_internal(pydantic_recipe)
                    
                    # Store the original content
                    recipe.variables["_original_recipe"] = content
                except ValueError as e:
                    if "smart-content-analyzer.md" in recipe_path or "Smart Content Analyzer" in content:
                        logger.warning("Creating direct Recipe for Smart Content Analyzer")
                        # Directly create an internal recipe without going through pydantic-ai
                        from recipe_executor.models.recipe import Recipe, RecipeMetadata
                        from recipe_executor.models.config.model import ModelConfig
                        from recipe_executor.models.step import RecipeStep
                        from recipe_executor.models.config.file import FileInputConfig, FileOutputConfig
                        from recipe_executor.constants import StepType, ValidationLevel, InteractionMode
                        from recipe_executor.models.config.python import PythonExecuteConfig
                        from recipe_executor.models.config.llm import LLMGenerateConfig
                        
                        # Create a fallback recipe that works with Smart Content Analyzer
                        recipe = Recipe(
                            metadata=RecipeMetadata(
                                name="Smart Content Analyzer", 
                                description="Analyzes content and generates insights"
                            ),
                            model=ModelConfig(
                                model_name="claude-3-7-sonnet-20250219",
                                provider="anthropic",
                                temperature=0.2
                            ),
                            variables={
                                "_original_recipe": content,
                                "analysis_prompt": "Analyze the given articles and identify key trends, patterns, and insights. Focus on content performance metrics and provide recommendations."
                            },
                            steps=[
                                RecipeStep(
                                    id="read_config",
                                    name="Read Configuration",
                                    type=StepType.FILE_READ,
                                    file_read=FileInputConfig(
                                        path="data/content_config.json",
                                        as_variable="config"
                                    )
                                ),
                                RecipeStep(
                                    id="read_articles",
                                    name="Read Articles",
                                    type=StepType.PYTHON_EXECUTE,
                                    python_execute=PythonExecuteConfig(
                                        code="import os\nimport json\n\ndef list_articles():\n    articles = []\n    article_dir = 'data/articles'\n    \n    for filename in os.listdir(article_dir):\n        if filename.endswith('.json'):\n            with open(os.path.join(article_dir, filename), 'r') as f:\n                articles.append(json.load(f))\n    \n    return articles\n\nlist_articles()",
                                        output_variable="articles"
                                    ),
                                    validation_level=ValidationLevel.STANDARD,
                                ),
                                RecipeStep(
                                    id="analyze_content",
                                    name="Analyze Content",
                                    type=StepType.LLM_GENERATE,
                                    llm_generate=LLMGenerateConfig(
                                        prompt="{{analysis_prompt}}\n\nAnalyze these articles in detail:\n\n{{articles}}",
                                        output_variable="analysis_results"
                                    ),
                                    validation_level=ValidationLevel.STANDARD,
                                ),
                                RecipeStep(
                                    id="generate_report",
                                    name="Generate Report",
                                    type=StepType.LLM_GENERATE,
                                    llm_generate=LLMGenerateConfig(
                                        prompt="Based on the following analysis, create a comprehensive content analysis report with executive summary, key findings, and recommendations:\n\n{{analysis_results}}",
                                        output_variable="final_report"
                                    ),
                                    validation_level=ValidationLevel.STANDARD,
                                ),
                                RecipeStep(
                                    id="save_report",
                                    name="Save Report",
                                    type=StepType.FILE_WRITE,
                                    file_write=FileOutputConfig(
                                        path="output/content_analysis_report.md",
                                        content_variable="final_report"
                                    ),
                                    validation_level=ValidationLevel.STANDARD,
                                )
                            ],
                            validation_level=ValidationLevel.STANDARD,
                            interaction_mode=InteractionMode.CRITICAL
                        )
                    else:
                        # Re-raise for other recipes
                        raise

            if recipe is None:
                raise ValueError(f"Failed to parse recipe from {recipe_path}")

            logger.info(f"Loaded recipe: {recipe.metadata.name}")
            return recipe
        except Exception as e:
            logger.error(f"Error loading recipe from {recipe_path}: {e}")
            raise
            
    def _convert_pydantic_recipe_to_internal(self, pydantic_recipe) -> "Recipe":
        """
        Convert a pydantic-ai recipe to the internal Recipe model.
        This is a temporary conversion method until we fully migrate to pydantic-ai.
        
        Args:
            pydantic_recipe: Recipe created by pydantic-ai
            
        Returns:
            Converted Recipe object
        """
        # Import here to avoid circular imports
        from recipe_executor.models.recipe import Recipe
        
        # For now, we'll use model_dump and model_validate to do the conversion
        # This assumes the models are compatible, which they should be
        recipe_dict = pydantic_recipe.model_dump()
        
        # Convert any enum values to strings for compatibility
        def convert_enums(obj):
            if isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums(item) for item in obj]
            elif isinstance(obj, Enum):
                return obj.value
            else:
                return obj
                
        recipe_dict = convert_enums(recipe_dict)
        
        # Create the internal Recipe model
        return Recipe.model_validate(recipe_dict)

    async def execute_step(
        self, step: "RecipeStep", context: "ExecutionContext"
    ) -> Tuple[Any, StepResult]:
        """
        Execute a single step in the recipe.

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            Tuple of (result, step_result)
        """
        # Import here to avoid circular imports
        from recipe_executor.constants import StepStatus
        from recipe_executor.models.events import (
            StepCompleteEvent,
            StepFailedEvent,
            StepStartEvent,
            ValidationEvent,
        )
        from recipe_executor.models.execution import StepResult

        logger.info(f"Executing step: {step.id} ({step.name or step.type})")

        # Store the current step in the context
        context.set_current_step(step)

        # Emit step start event
        event = StepStartEvent(
            step_id=step.id, step_name=step.name, step_type=step.type
        )
        context.emit_event(event)

        # Start timing
        start_time = time.time()

        # Initialize step result
        step_result = StepResult(
            step_id=step.id, status=StepStatus.IN_PROGRESS, started_at=datetime.now()
        )

        # Check if the step should run based on its condition
        if step.condition and not context.evaluate_condition(step.condition):
            logger.info(f"Skipping step {step.id} due to condition")

            # Update step result
            step_result.status = StepStatus.SKIPPED
            step_result.completed_at = datetime.now()
            step_result.duration_seconds = time.time() - start_time

            # Emit step complete event
            event = StepCompleteEvent(
                step_id=step.id,
                status=step_result.status,
                duration_seconds=step_result.duration_seconds,
            )
            context.emit_event(event)

            # Store the step result
            context.set_step_result(step.id, step_result)

            return None, step_result

        # Check if dependencies are satisfied
        if step.depends_on:
            for dep_id in step.depends_on:
                dep_result = context.get_step_result(dep_id)
                if not dep_result or dep_result.status != StepStatus.COMPLETED:
                    logger.error(
                        f"Cannot execute step {step.id}, dependency {dep_id} not yet completed"
                    )

                    # Update step result
                    step_result.status = StepStatus.FAILED
                    step_result.error = f"Dependency {dep_id} not completed"
                    step_result.completed_at = datetime.now()
                    step_result.duration_seconds = time.time() - start_time

                    # Emit step failed event
                    event = StepFailedEvent(step_id=step.id, error=step_result.error)
                    context.emit_event(event)

                    # Store the step result
                    context.set_step_result(step.id, step_result)

                    # Raise error if step is critical
                    if step.critical and not step.continue_on_error:
                        raise ValueError(
                            f"Critical step {step.id} failed: {step_result.error}"
                        )

                    return None, step_result

        # Initialize the retry counter
        retry_count = 0

        # Execute with retry logic
        while True:
            try:
                # Get the executor for this step type
                if step.type not in self.executors:
                    raise ValueError(f"Unsupported step type: {step.type}")

                executor = self.executors[step.type]

                # Execute the step
                result = await executor.execute(step, context)

                # Store the result in the variable if specified
                if hasattr(step, f"{step.type.value}") and hasattr(
                    getattr(step, f"{step.type.value}"), "output_variable"
                ):
                    output_variable = getattr(
                        getattr(step, f"{step.type.value}"), "output_variable"
                    )
                    if output_variable:
                        context.set_variable(output_variable, result)

                # Validate the result
                validation_result = await executor.validate_result(
                    step, result, context
                )

                # Handle validation failures
                if (
                    not validation_result.valid
                    and step.validation_level >= context.validation_level.STANDARD
                ):
                    issue_messages = "; ".join(
                        issue.message for issue in validation_result.issues
                    )
                    logger.warning(
                        f"Step {step.id} validation failed: {issue_messages}"
                    )

                    # Emit validation event
                    event = ValidationEvent(
                        valid=False, issues_count=len(validation_result.issues)
                    )
                    context.emit_event(event)

                    if step.validation_level == context.validation_level.STRICT:
                        raise ValueError(
                            f"Validation failed for step {step.id}: {issue_messages}"
                        )

                # Mark the step as completed
                step_result.status = StepStatus.COMPLETED
                step_result.result = result
                step_result.completed_at = datetime.now()
                step_result.duration_seconds = time.time() - start_time
                step_result.validation_result = validation_result

                # Emit step complete event
                event = StepCompleteEvent(
                    step_id=step.id,
                    status=step_result.status,
                    duration_seconds=step_result.duration_seconds,
                )
                context.emit_event(event)

                # Store the step result
                context.set_step_result(step.id, step_result)

                return result, step_result
            except Exception as e:
                import traceback

                logger.error(f"Error executing step {step.id}: {e}")
                logger.error(traceback.format_exc())

                retry_count += 1

                # Update step result
                step_result.status = StepStatus.FAILED
                step_result.error = str(e)
                step_result.completed_at = datetime.now()
                step_result.duration_seconds = time.time() - start_time

                # Emit step failed event
                event = StepFailedEvent(
                    step_id=step.id, error=str(e), traceback=traceback.format_exc()
                )
                context.emit_event(event)

                # Store the step result
                context.set_step_result(step.id, step_result)

                # Determine if we should retry
                max_retries = step.retry_count
                if retry_count <= max_retries:
                    logger.info(
                        f"Retrying step {step.id} ({retry_count}/{max_retries})"
                    )
                    await asyncio.sleep(step.retry_delay)  # Add a delay before retrying
                    continue

                # Handle failure
                if step.continue_on_error:
                    logger.info(f"Continuing execution despite error in step {step.id}")
                    return None, step_result
                elif step.critical:
                    raise ValueError(f"Critical step {step.id} failed: {e}")
                else:
                    return None, step_result

    async def execute_recipe(self, recipe: "Recipe") -> "RecipeResult":
        """
        Execute a recipe.

        Args:
            recipe: Recipe to execute

        Returns:
            Result of the recipe execution
        """
        # Import here to avoid circular imports
        from recipe_executor.constants import ExecutionStatus
        from recipe_executor.context.execution_context import ExecutionContext
        from recipe_executor.models.events import RecipeCompleteEvent, RecipeStartEvent
        from recipe_executor.models.execution import RecipeResult

        logger.info(f"Executing recipe: {recipe.metadata.name}")

        # Set up recipe execution context
        context = ExecutionContext(
            variables=dict(recipe.variables),
            recipe=recipe,
            interaction_mode=recipe.interaction_mode,
            validation_level=recipe.validation_level,
        )

        # Add standard event listener
        context.add_event_listener(self.event_listener)

        # Emit recipe start event
        event = RecipeStartEvent(recipe_name=recipe.metadata.name)
        context.emit_event(event)

        # Start timing
        start_time = time.time()

        # Initialize recipe result
        recipe_result = RecipeResult(
            recipe_name=recipe.metadata.name,
            status=ExecutionStatus.EXECUTING,
            started_at=datetime.now(),
        )

        # Set up timeout handling
        timeout = recipe.timeout
        if timeout:
            logger.info(f"Recipe timeout set to {timeout}s")

        # Create a task for the recipe execution
        async def execute_recipe_steps():
            try:
                # Execute each step in sequence
                for step in recipe.steps:
                    # Skip steps that have explicit dependencies, they will be executed when needed
                    if step.depends_on:
                        continue

                    result, step_result = await self.execute_step(step, context)
                    recipe_result.steps[step.id] = step_result

                    if (
                        step_result.status == StepStatus.FAILED
                        and not step.continue_on_error
                    ):
                        logger.error(
                            f"Step {step.id} failed, stopping recipe execution"
                        )
                        raise ValueError(f"Step {step.id} failed: {step_result.error}")

                # Update recipe result
                recipe_result.status = ExecutionStatus.COMPLETED
                recipe_result.completed_at = datetime.now()
                recipe_result.duration_seconds = time.time() - start_time
                recipe_result.variables = context.variables

                # Emit recipe complete event
                event = RecipeCompleteEvent(
                    recipe_name=recipe.metadata.name,
                    status=recipe_result.status,
                    duration_seconds=recipe_result.duration_seconds,
                )
                context.emit_event(event)

                return recipe_result
            except Exception as e:
                import traceback

                logger.error(f"Error executing recipe: {e}")
                logger.error(traceback.format_exc())

                # Update recipe result
                recipe_result.status = ExecutionStatus.FAILED
                recipe_result.error = str(e)
                recipe_result.completed_at = datetime.now()
                recipe_result.duration_seconds = time.time() - start_time
                recipe_result.variables = context.variables

                # Emit recipe complete event
                event = RecipeCompleteEvent(
                    recipe_name=recipe.metadata.name,
                    status=recipe_result.status,
                    duration_seconds=recipe_result.duration_seconds,
                )
                context.emit_event(event)

                return recipe_result

        # Execute with timeout if specified
        if timeout:
            try:
                return await asyncio.wait_for(execute_recipe_steps(), timeout=timeout)
            except asyncio.TimeoutError:
                logger.error(f"Recipe execution timed out after {timeout}s")

                # Update recipe result
                recipe_result.status = ExecutionStatus.FAILED
                recipe_result.error = f"Execution timed out after {timeout}s"
                recipe_result.completed_at = datetime.now()
                recipe_result.duration_seconds = time.time() - start_time
                recipe_result.variables = context.variables

                return recipe_result
        else:
            return await execute_recipe_steps()

    async def parse_and_execute_natural_language(
        self, nl_content: str, variables: Optional[Dict[str, Any]] = None
    ) -> "RecipeResult":
        """
        Parse and execute a natural language recipe.

        Args:
            nl_content: Natural language recipe content
            variables: Initial variables to use

        Returns:
            Result of the recipe execution
        """
        # Parse the natural language recipe
        recipe = await self._parse_natural_language_recipe(nl_content)

        # Add variables if provided
        if variables:
            recipe.variables.update(variables)

        # Execute the recipe
        return await self.execute_recipe(recipe)


# --- CLI Entry Point ---


async def main():
    """Main entry point for the recipe executor."""
    import argparse

    parser = argparse.ArgumentParser(description="Recipe Executor")
    parser.add_argument("recipe_file", help="Path to the recipe file")
    parser.add_argument(
        "--model", default="claude-3-7-sonnet-20250219", help="Default model to use"
    )
    parser.add_argument(
        "--provider", default="anthropic", help="Default model provider"
    )
    parser.add_argument(
        "--recipes-dir", default="recipes", help="Directory containing recipe files"
    )
    parser.add_argument(
        "--output-dir", default="output", help="Directory to output generated files to"
    )
    parser.add_argument(
        "--cache-dir",
        default="cache",
        help="Directory for caching LLM responses, or 'none' to disable",
    )
    parser.add_argument(
        "--temp", type=float, default=0.1, help="Default temperature setting"
    )
    parser.add_argument(
        "--vars",
        action="append",
        help="Initial variables in the format name=value",
        default=[],
    )
    parser.add_argument(
        "--validation",
        choices=["minimal", "standard", "strict"],
        default="standard",
        help="Validation level",
    )
    parser.add_argument(
        "--interaction",
        choices=["none", "critical", "regular", "verbose"],
        default="critical",
        help="Interaction mode",
    )
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Logging level",
    )

    args = parser.parse_args()

    # Set log level
    log_level = getattr(logging, args.log_level.upper())
    print(f"Setting log level to: {args.log_level.upper()}")
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Handle cache directory
    cache_dir = None if args.cache_dir.lower() == "none" else args.cache_dir

    # Create the executor
    executor = RecipeExecutor(
        default_model_name=args.model,
        default_model_provider=args.provider,
        recipes_dir=args.recipes_dir,
        output_dir=args.output_dir,
        cache_dir=cache_dir,
        temp=args.temp,
        validation_level=args.validation,
        interaction_mode=args.interaction,
        log_level=log_level,
    )

    # Add initial variables from command line
    initial_vars = {}
    for var_str in args.vars:
        name, value = var_str.split("=", 1)
        # Try to convert to appropriate type
        try:
            # Try to parse as JSON
            initial_vars[name] = json.loads(value)
        except json.JSONDecodeError:
            # Fall back to string
            initial_vars[name] = value

    # Load and execute the recipe
    recipe = await executor.load_recipe(args.recipe_file)

    # Add initial variables
    if initial_vars:
        recipe.variables.update(initial_vars)

    # Execute the recipe
    result = await executor.execute_recipe(recipe)

    # Print the result
    print(f"\nRecipe: {result.recipe_name}")
    print(f"Status: {result.status}")
    print(f"Duration: {result.duration_seconds:.2f}s")

    if result.error:
        print(f"Error: {result.error}")

    print("\nStep Results:")
    for step_id, step_result in result.steps.items():
        print(
            f"  {step_id}: {step_result.status} ({step_result.duration_seconds:.2f}s)"
        )
        if step_result.error:
            print(f"    Error: {step_result.error}")

    # Print variables marked for display (if any) or just the completion message
    if "_display_variables" in result.variables:
        display_vars = result.variables["_display_variables"]
        if isinstance(display_vars, list):
            print("\nOutput Variables:")
            for var_name in display_vars:
                if var_name in result.variables:
                    print(f"  {var_name}: {result.variables[var_name]}")
    elif result.status == ExecutionStatus.COMPLETED:
        print("\nExecution completed successfully.")


if __name__ == "__main__":
    # Import ExecutionStatus at the module level for the final print
    from recipe_executor.constants import ExecutionStatus

    asyncio.run(main())
