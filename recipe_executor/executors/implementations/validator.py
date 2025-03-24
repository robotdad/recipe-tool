"""Validator executor implementation."""

import json
import logging
from typing import Any

from recipe_executor.constants import OutputFormat, StepType
from recipe_executor.context.execution_context import ExecutionContext
from recipe_executor.models.events import ValidationEvent
from recipe_executor.models.step import RecipeStep
from recipe_executor.models.validation import ValidationIssue, ValidationResult

logger = logging.getLogger("recipe-executor")


class ValidatorExecutor:
    """Executor for validation steps."""

    async def execute(
        self, step: RecipeStep, context: ExecutionContext
    ) -> ValidationResult:
        """
        Execute a validation step.

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            Validation result
        """
        if not step.validator:
            raise ValueError(f"Missing validator configuration for step {step.id}")

        config = step.validator

        # Get the target variable
        target_var = context.get_variable(config.target_variable)
        if target_var is None:
            raise ValueError(f"Target variable {config.target_variable} not found")

        # Perform validation based on type
        if config.validation_type == "schema":
            # Schema validation
            if not config.validation_schema:
                raise ValueError("Schema validation requires a schema")

            try:
                from jsonschema import (
                    ValidationError as JsonSchemaValidationError,
                )
                from jsonschema import (
                    validate,
                )

                try:
                    validate(instance=target_var, schema=config.validation_schema)
                    result = ValidationResult(valid=True, issues=[])
                except JsonSchemaValidationError as e:
                    result = ValidationResult(
                        valid=False,
                        issues=[
                            ValidationIssue(
                                message=config.error_message
                                or f"Schema validation failed: {e.message}",
                                severity="error",
                                path=".".join(str(p) for p in e.path)
                                if e.path
                                else None,
                            )
                        ],
                    )
            except ImportError:
                logger.warning(
                    "jsonschema package not installed, validation will be skipped"
                )
                result = ValidationResult(
                    valid=False,
                    issues=[
                        ValidationIssue(
                            message="jsonschema package not installed, validation was skipped",
                            severity="warning",
                        )
                    ],
                )
        elif config.validation_type == "code":
            # Code validation
            if not config.code:
                raise ValueError("Code validation requires code")

            try:
                # Common imports that might be needed
                import re
                from datetime import datetime

                validation_globals = {
                    "target": target_var,
                    "valid": True,
                    "issues": [],
                    "json": json,
                    "datetime": datetime,
                    "re": re,
                }

                exec(config.code, validation_globals, {})

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

                result = ValidationResult(valid=valid, issues=validation_issues)
            except Exception as e:
                logger.error(f"Error in validation code: {e}")
                result = ValidationResult(
                    valid=False,
                    issues=[
                        ValidationIssue(
                            message=config.error_message
                            or f"Error in validation code: {e}",
                            severity="error",
                        )
                    ],
                )
        elif config.validation_type == "llm":
            # LLM validation
            if not config.llm_prompt:
                raise ValueError("LLM validation requires a prompt")

            # Create an LLM executor
            from recipe_executor.executors.implementations.llm import (
                LLMGenerateExecutor,
            )
            from recipe_executor.models.config.llm import LLMGenerateConfig

            llm_executor = LLMGenerateExecutor()

            # Create a temporary step for the LLM validation
            llm_step = RecipeStep(
                id=f"{step.id}_llm",
                type=StepType.LLM_GENERATE,
                llm_generate=LLMGenerateConfig(
                    prompt=config.llm_prompt.replace(
                        "${target}",
                        json.dumps(target_var)
                        if isinstance(target_var, (dict, list))
                        else str(target_var),
                    ),
                    output_format=OutputFormat.STRUCTURED,
                    output_variable="_validation_result",
                    structured_schema={
                        "title": "ValidationResult",
                        "type": "object",
                        "properties": {
                            "valid": {"type": "boolean"},
                            "issues": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "message": {"type": "string"},
                                        "severity": {
                                            "type": "string",
                                            "enum": ["error", "warning", "info"],
                                        },
                                        "path": {"type": "string"},
                                    },
                                    "required": ["message", "severity"],
                                },
                            },
                        },
                        "required": ["valid", "issues"],
                    },
                ),
            )

            # Execute the LLM validation
            llm_result = await llm_executor.execute(llm_step, context)

            # Convert to ValidationResult
            if isinstance(llm_result, dict) and "valid" in llm_result:
                valid = llm_result.get("valid", True)
                issues = llm_result.get("issues", [])

                validation_issues = []
                for issue in issues:
                    validation_issues.append(
                        ValidationIssue(
                            message=issue.get("message", "Unknown issue"),
                            severity=issue.get("severity", "error"),
                            path=issue.get("path"),
                        )
                    )

                result = ValidationResult(valid=valid, issues=validation_issues)
            else:
                result = ValidationResult(
                    valid=False,
                    issues=[
                        ValidationIssue(
                            message=config.error_message
                            or "LLM validation failed to return a valid result",
                            severity="error",
                        )
                    ],
                )
        else:
            raise ValueError(f"Unsupported validation type: {config.validation_type}")

        # Store the result in the output variable
        if config.output_variable:
            context.set_variable(config.output_variable, result)

        # Emit validation event
        event = ValidationEvent(valid=result.valid, issues_count=len(result.issues))
        context.emit_event(event)

        return result

    async def validate_result(
        self, step: RecipeStep, result: Any, context: ExecutionContext
    ) -> ValidationResult:
        """
        Validate the result of a validation step.

        Args:
            step: Step to validate
            result: Result to validate
            context: Execution context

        Returns:
            Validation result
        """
        # The result is already a ValidationResult
        return ValidationResult(valid=True, issues=[])
