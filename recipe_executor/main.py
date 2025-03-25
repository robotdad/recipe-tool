"""Main RecipeExecutor class and CLI entry point."""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from recipe_executor.constants import (
    DEFAULT_MODEL_NAME,
    DEFAULT_MODEL_PROVIDER,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_RECIPES_DIR,
    DEFAULT_TEMPERATURE,
    ExecutionStatus,
    InteractionMode,
    ProviderType,
    StepStatus,
    StepType,
    ValidationLevel,
)
from recipe_executor.context.execution_context import ExecutionContext
from recipe_executor.events.event_system import EventSystem
from recipe_executor.events.listeners.console import ConsoleEventListener
from recipe_executor.models.events import (
    RecipeCompleteEvent,
    RecipeStartEvent,
    StepCompleteEvent,
    StepFailedEvent,
    StepStartEvent,
)
from recipe_executor.models.execution import RecipeResult, StepResult
from recipe_executor.models.recipe import Recipe
from recipe_executor.models.step import RecipeStep
from recipe_executor.parsers.formats import load_recipe_file, parse_natural_language
from recipe_executor.utils import logging as log_utils

# Setup logging
logger = log_utils.get_logger()


class RecipeExecutor:
    """
    Main class for executing LLM recipes with code-driven reliability.
    """

    def __init__(
        self,
        default_model_name: str = DEFAULT_MODEL_NAME,
        default_model_provider: str = DEFAULT_MODEL_PROVIDER,
        recipes_dir: str = DEFAULT_RECIPES_DIR,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        temp: float = DEFAULT_TEMPERATURE,
        validation_level: Optional[Union[str, ValidationLevel]] = ValidationLevel.STANDARD,
        interaction_mode: Optional[Union[str, InteractionMode]] = InteractionMode.CRITICAL,
        log_level: int = logging.INFO,
    ):
        """
        Initialize the recipe executor.

        Args:
            default_model_name: The default model name to use
            default_model_provider: The default provider of the model
            recipes_dir: Directory containing recipe files
            output_dir: Directory to output generated files to
            temp: Default temperature setting for the model
            validation_level: Default validation level
            interaction_mode: Default interaction mode
            log_level: Logging level
        """
        # Import step executors to avoid circular imports
        from recipe_executor.executors.implementations.api import ApiCallExecutor
        from recipe_executor.executors.implementations.chain import ChainExecutor
        from recipe_executor.executors.implementations.conditional import ConditionalExecutor
        from recipe_executor.executors.implementations.file import FileReadExecutor, FileWriteExecutor
        from recipe_executor.executors.implementations.input import WaitForInputExecutor
        from recipe_executor.executors.implementations.json import JsonProcessExecutor
        from recipe_executor.executors.implementations.llm import LLMGenerateExecutor
        from recipe_executor.executors.implementations.parallel import ParallelExecutor
        from recipe_executor.executors.implementations.python import PythonExecuteExecutor
        from recipe_executor.executors.implementations.template import TemplateSubstituteExecutor
        from recipe_executor.executors.implementations.validator import ValidatorExecutor

        self.default_model_name = default_model_name
        self.default_model_provider = default_model_provider
        self.recipes_dir = recipes_dir
        self.output_dir = output_dir
        self.temp = temp

        # Convert string values to enums if needed
        if isinstance(validation_level, str):
            self.validation_level = ValidationLevel[validation_level.upper()]
        else:
            self.validation_level = validation_level

        if isinstance(interaction_mode, str):
            self.interaction_mode = InteractionMode[interaction_mode.upper()]
        else:
            self.interaction_mode = interaction_mode

        # Initialize logging
        log_manager = log_utils.LogManager(reset_logs=True)
        log_manager.set_level(log_level)

        # Create required directories
        os.makedirs(output_dir, exist_ok=True)

        # Setup environment and check API keys
        self._load_environment()
        self._check_api_keys()

        # Initialize the event system
        self.event_system = EventSystem()
        self.event_system.add_listener(ConsoleEventListener())

        # Initialize the executors for each step type
        self.executors = {
            StepType.LLM_GENERATE: LLMGenerateExecutor(),
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

    def _load_environment(self) -> None:
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
                    logger.info("No .env file found. Using environment variables directly.")
        except ImportError:
            logger.warning("python-dotenv not installed. Environment variables must be set in the environment.")
            logger.warning("Install with: pip install python-dotenv")

    def _check_api_keys(self) -> None:
        """Check if required API keys are available and exit if the default provider's key is missing."""
        from recipe_executor.utils.authentication import AuthManager
        
        # Create auth manager
        auth_manager = AuthManager()
        
        # Verify the default provider's API key
        is_valid, error_message = auth_manager.verify_api_key(self.default_model_provider)
        
        if not is_valid:
            logger.error(f"API key validation failed: {error_message}")
            print("\n" + "=" * 80)
            print(f"\033[1;31mError:\033[0m {error_message}")
            print("=" * 80)
            
            # Get detailed instructions for setting up the API key
            instructions = auth_manager.get_api_key_instructions(self.default_model_provider)
            print(f"\n{instructions}")
            print("\nOnce you've set up your API key, run the command again.\n")
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

        # Try loading from structured formats
        try:
            # This handles YAML, JSON, and structured markdown
            return load_recipe_file(recipe_path, Recipe)
        except ValueError as e:
            # If it's a format that requires async parsing, or an error occurred
            if "requires async parsing" in str(e):
                # Read the file content
                with open(recipe_path, "r") as f:
                    content = f.read()
                
                return await parse_natural_language(
                    content,
                    Recipe,
                    self.default_model_name,
                    self.default_model_provider,
                    self.temp
                )
            else:
                # Re-raise other errors
                raise

    async def execute_step(self, step: RecipeStep, context: ExecutionContext) -> Tuple[Any, StepResult]:
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

        # Emit step start event
        event = StepStartEvent(step_id=step.id, step_name=step.name, step_type=step.type)
        self.event_system.emit(event)

        # Start timing
        start_time = time.time()

        # Initialize step result
        step_result = StepResult(step_id=step.id, status=StepStatus.IN_PROGRESS, started_at=datetime.now())

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
            self.event_system.emit(event)

            # Store the step result
            context.set_step_result(step.id, step_result)

            return None, step_result

        # Check if dependencies are satisfied
        if step.depends_on:
            for dep_id in step.depends_on:
                dep_result = context.get_step_result(dep_id)
                if not dep_result or dep_result.status != StepStatus.COMPLETED:
                    logger.error(f"Cannot execute step {step.id}, dependency {dep_id} not yet completed")

                    # Update step result
                    step_result.status = StepStatus.FAILED
                    step_result.error = f"Dependency {dep_id} not completed"
                    step_result.completed_at = datetime.now()
                    step_result.duration_seconds = time.time() - start_time

                    # Emit step failed event
                    event = StepFailedEvent(step_id=step.id, error=step_result.error)
                    self.event_system.emit(event)

                    # Store the step result
                    context.set_step_result(step.id, step_result)

                    # Raise error if step is critical
                    if step.critical and not step.continue_on_error:
                        raise ValueError(f"Critical step {step.id} failed: {step_result.error}")

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
                config_attr = getattr(step, step.type.value, None)
                if config_attr and hasattr(config_attr, "output_variable"):
                    output_variable = getattr(config_attr, "output_variable", None)
                    if output_variable:
                        context.set_variable(output_variable, result)

                # Validation is simplified - we'll run the executor's validate_result if available
                validation_result = None
                if hasattr(executor, "validate_result"):
                    validation_result = await executor.validate_result(step, result, context)
                    step_result.validation_result = validation_result

                # Mark the step as completed
                step_result.status = StepStatus.COMPLETED
                step_result.result = result
                step_result.completed_at = datetime.now()
                step_result.duration_seconds = time.time() - start_time

                # Emit step complete event
                event = StepCompleteEvent(
                    step_id=step.id,
                    status=step_result.status,
                    duration_seconds=step_result.duration_seconds,
                )
                self.event_system.emit(event)

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
                event = StepFailedEvent(step_id=step.id, error=str(e), traceback=traceback.format_exc())
                self.event_system.emit(event)

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

        # Set up recipe execution context - handle None values for compatibility
        interaction_mode = recipe.interaction_mode or self.interaction_mode
        if interaction_mode is None:
            interaction_mode = InteractionMode.CRITICAL
            
        validation_level = recipe.validation_level or self.validation_level
        if validation_level is None:
            validation_level = ValidationLevel.STANDARD
            
        context = ExecutionContext(
            variables=dict(recipe.variables),
            recipe=recipe,
            interaction_mode=interaction_mode,
            validation_level=validation_level,
            event_system=self.event_system,
        )

        # Emit recipe start event
        event = RecipeStartEvent(
            recipe_name=recipe.metadata.name,
            description=recipe.metadata.description or "",
        )
        self.event_system.emit(event)

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
                recipe_result.variables = context.get_all_variables()

                # Emit recipe complete event
                event = RecipeCompleteEvent(
                    recipe_name=recipe.metadata.name,
                    status=recipe_result.status,
                    duration_seconds=recipe_result.duration_seconds,
                )
                self.event_system.emit(event)

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
                recipe_result.variables = context.get_all_variables()

                # Emit recipe complete event (failed)
                event = RecipeCompleteEvent(
                    recipe_name=recipe.metadata.name,
                    status=recipe_result.status,
                    duration_seconds=recipe_result.duration_seconds,
                    error=str(e),
                )
                self.event_system.emit(event)

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
                recipe_result.variables = context.get_all_variables()

                # Emit recipe complete event (timeout)
                event = RecipeCompleteEvent(
                    recipe_name=recipe.metadata.name,
                    status=recipe_result.status,
                    duration_seconds=recipe_result.duration_seconds,
                    error=recipe_result.error,
                )
                self.event_system.emit(event)

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
            self.temp
        )

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
    parser.add_argument("--model", default=DEFAULT_MODEL_NAME, help="Default model to use")
    parser.add_argument("--provider", default=DEFAULT_MODEL_PROVIDER, help="Default model provider")
    parser.add_argument("--recipes-dir", default=DEFAULT_RECIPES_DIR, help="Directory containing recipe files")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Directory to output generated files to")
    parser.add_argument("--temp", type=float, default=DEFAULT_TEMPERATURE, help="Default temperature setting")
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


    # Create the executor
    executor = RecipeExecutor(
        default_model_name=args.model,
        default_model_provider=args.provider,
        recipes_dir=args.recipes_dir,
        output_dir=args.output_dir,
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

    # Print variables marked for display (if any)
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
    asyncio.run(main())