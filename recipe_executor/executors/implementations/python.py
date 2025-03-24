"""Python execution executor implementation."""

import asyncio
import concurrent.futures
import logging
from typing import Any

from recipe_executor.context.execution_context import ExecutionContext
from recipe_executor.models.step import RecipeStep
from recipe_executor.models.validation import ValidationIssue, ValidationResult

logger = logging.getLogger("recipe-executor")


class PythonExecuteExecutor:
    """Executor for Python execution steps."""

    async def execute(self, step: RecipeStep, context: ExecutionContext) -> Any:
        """
        Execute a Python execute step.

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            Result of the Python execution
        """
        if not step.python_execute:
            raise ValueError(f"Missing python_execute configuration for step {step.id}")

        config = step.python_execute

        # Get the code to execute
        if config.code_file:
            code_file = context.interpolate_variables(config.code_file)
            try:
                with open(code_file, "r") as f:
                    code = f.read()
            except Exception as e:
                logger.error(f"Error reading code file {code_file}: {e}")
                if not step.continue_on_error:
                    raise
                return None
        else:
            code = config.code

        # Prepare the execution context
        exec_globals = {
            "json": __import__("json"),
            "os": __import__("os"),
            "datetime": __import__("datetime"),
            "re": __import__("re"),
            "math": __import__("math"),
            "random": __import__("random"),
            "collections": __import__("collections"),
            "functools": __import__("functools"),
            "itertools": __import__("itertools"),
            "result": None,  # This will be set by the code
        }

        # Add input variables to the context
        for var_name, var_source in config.input_variables.items():
            var_source = context.interpolate_variables(var_source)
            var_value = context.get_variable(var_source)
            if var_value is not None:
                exec_globals[var_name] = var_value
            else:
                exec_globals[var_name] = var_source

        # Apply import restrictions if specified
        original_import = None
        if config.allowed_imports:
            original_import = __builtins__.__import__

            def restricted_import(name, *args, **kwargs):
                if name in config.allowed_imports:
                    return original_import(name, *args, **kwargs)
                else:
                    raise ImportError(f"Import of {name} is not allowed")

            __builtins__.__import__ = restricted_import

        # Set up timeout handling
        timeout = config.timeout
        if timeout is None and step.timeout:
            timeout = step.timeout
        if timeout is None and context.recipe and context.recipe.timeout:
            timeout = context.recipe.timeout

        # Set up memory limit if specified
        if config.memory_limit_mb:
            # This is a simple approximation and not a hard limit
            try:
                import resource

                resource.setrlimit(
                    resource.RLIMIT_AS, (config.memory_limit_mb * 1024 * 1024, -1)
                )
            except (ImportError, AttributeError):
                logger.warning("Memory limit not supported on this platform")

        # Execute the code with timeout
        try:
            if timeout:
                try:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(exec, code, exec_globals, {})
                        result = await asyncio.get_event_loop().run_in_executor(
                            None, lambda: future.result(timeout=timeout)
                        )
                except concurrent.futures.TimeoutError:
                    logger.error(
                        f"Python execution timed out after {timeout}s for step {step.id}"
                    )
                    raise TimeoutError(f"Python execution timed out after {timeout}s")
            else:
                exec(code, exec_globals, {})
        finally:
            # Restore original import if it was modified
            if original_import is not None:
                __builtins__.__import__ = original_import

        result = exec_globals.get("result")
        return result

    async def validate_result(
        self, step: RecipeStep, result: Any, context: ExecutionContext
    ) -> ValidationResult:
        """
        Validate the result of a Python execute step.

        Args:
            step: Step to validate
            result: Result to validate
            context: Execution context

        Returns:
            Validation result
        """
        if not step.python_execute:
            return ValidationResult(valid=True, issues=[])

        config = step.python_execute

        # Run validation code if provided
        if config.validation_code:
            try:
                # Get required imports
                import json
                import re
                from datetime import datetime

                validation_globals = {
                    "result": result,
                    "valid": True,
                    "issues": [],
                    "json": json,
                    "datetime": datetime,
                    "re": re,
                }

                exec(config.validation_code, validation_globals, {})

                valid = validation_globals.get("valid", True)
                issues = validation_globals.get("issues", [])

                validation_issues = []
                for issue in issues:
                    if isinstance(issue, dict):
                        validation_issues.append(
                            ValidationIssue(
                                message=issue.get("message", "Unknown issue"),
                                severity=issue.get("severity", "error"),
                                path=issue.get("path"),
                            )
                        )
                    else:
                        validation_issues.append(
                            ValidationIssue(message=str(issue), severity="error")
                        )

                return ValidationResult(valid=valid, issues=validation_issues)
            except Exception as e:
                logger.error(f"Error in validation code: {e}")
                return ValidationResult(
                    valid=False,
                    issues=[
                        ValidationIssue(
                            message=f"Error in validation code: {e}", severity="error"
                        )
                    ],
                )

        return ValidationResult(valid=True, issues=[])
