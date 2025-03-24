"""File operation executors implementation."""

import glob
import json
import logging
import os
from typing import Any

from recipe_executor.context.execution_context import ExecutionContext
from recipe_executor.models.step import RecipeStep
from recipe_executor.models.validation import ValidationIssue, ValidationResult

logger = logging.getLogger("recipe-executor")


class FileReadExecutor:
    """Executor for file read steps."""

    async def execute(self, step: RecipeStep, context: ExecutionContext) -> Any:
        """
        Execute a file read step.

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            File content
        """
        if not step.file_read:
            raise ValueError(f"Missing file_read configuration for step {step.id}")

        config = step.file_read
        path = context.interpolate_variables(config.path)

        if config.pattern:
            pattern = context.interpolate_variables(config.pattern)
            file_paths = glob.glob(os.path.join(os.path.dirname(path), pattern))
            if not file_paths:
                logger.warning(f"No files found matching pattern {pattern}")
                return {}

            # Read all matching files
            contents = {}
            for file_path in file_paths:
                try:
                    with open(file_path, "r", encoding=config.encoding) as f:
                        contents[os.path.basename(file_path)] = f.read()
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")
                    if not step.continue_on_error:
                        raise

            return contents
        else:
            # Read a single file
            try:
                with open(path, "r", encoding=config.encoding) as f:
                    content = f.read()

                return content
            except Exception as e:
                logger.error(f"Error reading file {path}: {e}")
                if not step.continue_on_error:
                    raise
                return None

    async def validate_result(
        self, step: RecipeStep, result: Any, context: ExecutionContext
    ) -> ValidationResult:
        """
        Validate the result of a file read step.

        Args:
            step: Step to validate
            result: Result to validate
            context: Execution context

        Returns:
            Validation result
        """
        if not step.file_read:
            return ValidationResult(valid=True, issues=[])

        config = step.file_read

        # For pattern-based file reading, check that at least one file was found
        if config.pattern and isinstance(result, dict) and not result:
            return ValidationResult(
                valid=False,
                issues=[
                    ValidationIssue(
                        message=f"No files found matching pattern {config.pattern}",
                        severity="error",
                    )
                ],
            )

        # For single file reading, check that the file was read
        if not config.pattern and result is None:
            return ValidationResult(
                valid=False,
                issues=[
                    ValidationIssue(
                        message=f"Failed to read file {config.path}", severity="error"
                    )
                ],
            )

        return ValidationResult(valid=True, issues=[])


class FileWriteExecutor:
    """Executor for file write steps."""

    async def execute(self, step: RecipeStep, context: ExecutionContext) -> bool:
        """
        Execute a file write step.

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            True if the file was written successfully
        """
        if not step.file_write:
            raise ValueError(f"Missing file_write configuration for step {step.id}")

        config = step.file_write
        path = context.interpolate_variables(config.path)

        content_var = context.get_variable(config.content_variable)
        if content_var is None:
            raise ValueError(f"Content variable {config.content_variable} not found")

        content = content_var
        if not isinstance(content, str):
            # Try to convert to string
            if isinstance(content, (dict, list)):
                content = json.dumps(content, indent=2)
            else:
                content = str(content)

        # Create directory if needed
        if config.mkdir:
            os.makedirs(os.path.dirname(path), exist_ok=True)

        try:
            with open(path, config.mode, encoding=config.encoding) as f:
                f.write(content)

            logger.info(f"Wrote file: {path}")
            return True
        except Exception as e:
            logger.error(f"Error writing file {path}: {e}")
            if not step.continue_on_error:
                raise
            return False

    async def validate_result(
        self, step: RecipeStep, result: Any, context: ExecutionContext
    ) -> ValidationResult:
        """
        Validate the result of a file write step.

        Args:
            step: Step to validate
            result: Result to validate
            context: Execution context

        Returns:
            Validation result
        """
        if not step.file_write:
            return ValidationResult(valid=True, issues=[])

        config = step.file_write
        path = context.interpolate_variables(config.path)

        # Check that the file was written
        if not result:
            return ValidationResult(
                valid=False,
                issues=[
                    ValidationIssue(
                        message=f"Failed to write file {path}", severity="error"
                    )
                ],
            )

        # Check that the file exists
        if not os.path.exists(path):
            return ValidationResult(
                valid=False,
                issues=[
                    ValidationIssue(
                        message=f"File {path} does not exist after write operation",
                        severity="error",
                    )
                ],
            )

        return ValidationResult(valid=True, issues=[])
