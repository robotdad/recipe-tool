"""Core RecipeExecutor implementation with the simplified architecture."""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Tuple

from recipe_executor.constants import ExecutionStatus, StepStatus, StepType
from recipe_executor.context.simple_context import ExecutionContext
from recipe_executor.models.step import RecipeStep
from recipe_executor.executors.registry import get_executor
from recipe_executor.models.execution import RecipeResult, StepResult
from recipe_executor.models.recipe import Recipe
from recipe_executor.parsers.formats import (
    extract_structured_content,
    load_from_json,
    load_from_yaml,
    parse_natural_language,
)
from recipe_executor.utils import logging as log_utils
from recipe_executor.utils.progress import (
    ProgressEvent,
    ProgressTracker,
    create_console_reporter,
    create_structured_logger,
)

logger = log_utils.get_logger()


class RecipeExecutor:
    """
    Simplified recipe executor with functional design.
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
        from recipe_executor.constants import InteractionMode, ValidationLevel

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

        # Create progress tracker
        self.progress = ProgressTracker()
        self.progress.add_callback(create_console_reporter())
        self.progress.add_callback(create_structured_logger())

        # Import executor functions to ensure they're registered
        self._import_executors()

    def _import_executors(self):
        """Import all executor functions to ensure they're registered."""
        # This will trigger the registration of all executors
        import recipe_executor.executors.functions.file
        import recipe_executor.executors.functions.llm
        import recipe_executor.executors.functions.python
        # Add other executor imports as they're implemented

    def _load_environment(self):
        """Load environment variables from .env files."""
        try:
            from dotenv import load_dotenv
            from pathlib import Path

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
        """Check if required API keys are available and exit if the default provider's key is missing."""
        from recipe_executor.utils.authentication import AuthManager

        # Create auth manager
        auth_manager = AuthManager()

        # Verify the default provider's API key
        is_valid, error_message = auth_manager.verify_api_key(
            self.default_model_provider
        )

        if not is_valid:
            logger.error(f"API key validation failed: {error_message}")
            print("\n" + "=" * 80)
            print(f"\033[1;31mError:\033[0m {error_message}")
            print("=" * 80)

            # Get detailed instructions for setting up the API key
            instructions = auth_manager.get_api_key_instructions(
                self.default_model_provider
            )
            print(f"\n{instructions}")
            print("\nOnce you've set up your API key, run the command again.\n")
            import sys
            sys.exit(1)

    async def load_recipe(self, recipe_path: str) -> Recipe:
        """
        Load a recipe from a file.

        Args:
            recipe_path: Path to the recipe file

        Returns:
            Recipe object
        """
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

            recipe = None

            # Try to parse based on file extension
            if file_ext == ".json":
                try:
                    recipe = load_from_json(content, Recipe)
                except Exception as e:
                    logger.info(f"JSON parsing failed, treating as natural language: {e}")
            elif file_ext in [".yaml", ".yml"]:
                try:
                    recipe = load_from_yaml(content, Recipe)
                except Exception as e:
                    logger.info(f"YAML parsing failed, treating as natural language: {e}")
            elif file_ext == ".md":
                # For markdown files, try to extract YAML/JSON from code blocks
                structured_data = extract_structured_content(content)
                if structured_data:
                    try:
                        recipe = Recipe.model_validate(structured_data)
                    except Exception as e:
                        logger.info(f"Structured markdown parsing failed: {e}")

            # If not parsed as structured format, use natural language parsing
            if recipe is None:
                logger.info("Parsing as natural language recipe")
                recipe = await parse_natural_language(
                    content,
                    Recipe,
                    self.default_model_name,
                    self.default_model_provider,
                    self.temp,
                )

            if recipe is None:
                raise ValueError(f"Failed to parse recipe from {recipe_path}")

            logger.info(f"Loaded recipe: {recipe.metadata.name}")
            return recipe
        except Exception as e:
            logger.error(f"Error loading recipe from {recipe_path}: {e}")
            raise

    async def execute_step(
        self, step: "RecipeStep", context: ExecutionContext
    ) -> Tuple[Any, StepResult]:
        """
        Execute a single step in the recipe.

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            Tuple of (result, step_result)
        """
        logger.info(f"Executing step: {step.id} ({step.name or step.type})")

        # Store the current step in the context
        context.set_current_step(step)

        # Notify of step start
        self.progress.notify(
            ProgressEvent.STEP_START,
            {
                "step_id": step.id,
                "step_name": step.name or "",
                "step_type": step.type.value,
            },
        )

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

            # Notify of step skip
            self.progress.notify(
                ProgressEvent.STEP_SKIPPED,
                {
                    "step_id": step.id,
                    "condition": step.condition,
                    "duration_seconds": step_result.duration_seconds,
                },
            )

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

                    # Notify of step failure
                    self.progress.notify(
                        ProgressEvent.STEP_FAILED,
                        {
                            "step_id": step.id,
                            "error": step_result.error,
                            "duration_seconds": step_result.duration_seconds,
                        },
                    )

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
                executor = get_executor(step.type)

                # Execute the step
                result = await executor(step, context)

                # Store the result in the variable if specified
                if hasattr(step, f"{step.type.value}") and hasattr(
                    getattr(step, f"{step.type.value}"), "output_variable"
                ):
                    output_variable = getattr(
                        getattr(step, f"{step.type.value}"), "output_variable"
                    )
                    if output_variable:
                        # With our new immutable context, we need to create a new one
                        context = context.with_variable(output_variable, result)

                # For now, skip validation since we're simplifying
                # We'll add it back later in a more streamlined form

                # Mark the step as completed
                step_result.status = StepStatus.COMPLETED
                step_result.result = result
                step_result.completed_at = datetime.now()
                step_result.duration_seconds = time.time() - start_time

                # Notify of step completion
                self.progress.notify(
                    ProgressEvent.STEP_COMPLETE,
                    {
                        "step_id": step.id,
                        "status": step_result.status.value,
                        "duration_seconds": step_result.duration_seconds,
                    },
                )

                # Store the step result in the context
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

                # Notify of step failure
                self.progress.notify(
                    ProgressEvent.STEP_FAILED,
                    {
                        "step_id": step.id,
                        "error": str(e),
                        "duration_seconds": step_result.duration_seconds,
                        "traceback": traceback.format_exc(),
                    },
                )

                # Store the step result
                context.set_step_result(step.id, step_result)

                # Determine if we should retry
                max_retries = step.retry_count
                if retry_count <= max_retries:
                    logger.info(f"Retrying step {step.id} ({retry_count}/{max_retries})")
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

    async def execute_recipe(self, recipe: Recipe) -> RecipeResult:
        """
        Execute a recipe.

        Args:
            recipe: Recipe to execute

        Returns:
            Result of the recipe execution
        """
        logger.info(f"Executing recipe: {recipe.metadata.name}")

        # Set up recipe execution context
        context = ExecutionContext(
            variables=dict(recipe.variables),
            recipe=recipe,
            interaction_mode=recipe.interaction_mode,
            validation_level=recipe.validation_level,
            cache_dir=self.cache_dir,
        )

        # Notify of recipe start
        self.progress.notify(
            ProgressEvent.RECIPE_START,
            {
                "recipe_name": recipe.metadata.name,
                "description": recipe.metadata.description,
                "step_count": len(recipe.steps),
            },
        )

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

                    if step_result.status == StepStatus.FAILED and not step.continue_on_error:
                        logger.error(f"Step {step.id} failed, stopping recipe execution")
                        raise ValueError(f"Step {step.id} failed: {step_result.error}")

                # Update recipe result
                recipe_result.status = ExecutionStatus.COMPLETED
                recipe_result.completed_at = datetime.now()
                recipe_result.duration_seconds = time.time() - start_time
                recipe_result.variables = context._variables  # Access private field directly

                # Notify of recipe completion
                self.progress.notify(
                    ProgressEvent.RECIPE_COMPLETE,
                    {
                        "recipe_name": recipe.metadata.name,
                        "status": recipe_result.status.value,
                        "duration_seconds": recipe_result.duration_seconds,
                    },
                )

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
                recipe_result.variables = context._variables

                # Notify of recipe completion (with failure)
                self.progress.notify(
                    ProgressEvent.RECIPE_COMPLETE,
                    {
                        "recipe_name": recipe.metadata.name,
                        "status": recipe_result.status.value,
                        "duration_seconds": recipe_result.duration_seconds,
                        "error": str(e),
                    },
                )

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
                
                # Get variables from context (might be incomplete)
                recipe_result.variables = context._variables

                return recipe_result
        else:
            return await execute_recipe_steps()

    async def parse_and_execute_natural_language(
        self, nl_content: str, variables: Optional[Dict[str, Any]] = None
    ) -> RecipeResult:
        """
        Parse and execute a natural language recipe.

        Args:
            nl_content: Natural language recipe content
            variables: Initial variables to use

        Returns:
            Result of the recipe execution
        """
        # Parse the natural language recipe
        recipe = await parse_natural_language(
            nl_content,
            Recipe,
            self.default_model_name,
            self.default_model_provider,
            self.temp,
        )

        # Add variables if provided
        if variables:
            recipe.variables.update(variables)

        # Execute the recipe
        return await self.execute_recipe(recipe)