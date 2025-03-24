"""Validation utilities for Recipe Executor."""

import logging
from typing import Any, Dict, List, Tuple

from recipe_executor.models.validation import ValidationIssue, ValidationResult

logger = logging.getLogger("recipe-executor")


def validate_schema(
    data: Any, schema: Dict[str, Any]
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Validate data against a JSON schema.

    Args:
        data: Data to validate
        schema: JSON schema to validate against

    Returns:
        Tuple of (is_valid, list of issues)
    """
    try:
        from jsonschema import ValidationError, validate

        try:
            validate(instance=data, schema=schema)
            return True, []
        except ValidationError as e:
            issue = {
                "message": e.message,
                "path": ".".join(str(p) for p in e.path) if e.path else None,
                "severity": "error",
            }
            return False, [issue]
    except ImportError:
        logger.warning("jsonschema package not installed, validation will be skipped")
        return False, [
            {"message": "jsonschema package not installed", "severity": "warning"}
        ]


def validate_values(
    data: Dict[str, Any], rules: Dict[str, Dict[str, Any]]
) -> ValidationResult:
    """
    Validate data values against business rules.

    Args:
        data: Data to validate
        rules: Dict of rules to apply, key is field name

    Returns:
        ValidationResult
    """
    issues = []

    for field, field_rules in rules.items():
        value = data.get(field)

        # Required check
        if field_rules.get("required", False) and value is None:
            issues.append(
                ValidationIssue(
                    message=f"Field '{field}' is required", severity="error", path=field
                )
            )
            continue

        # Skip other validations if value is None
        if value is None:
            continue

        # Type check
        expected_type = field_rules.get("type")
        if expected_type:
            if expected_type == "string" and not isinstance(value, str):
                issues.append(
                    ValidationIssue(
                        message=f"Field '{field}' must be a string",
                        severity="error",
                        path=field,
                    )
                )
            elif expected_type == "number" and not isinstance(value, (int, float)):
                issues.append(
                    ValidationIssue(
                        message=f"Field '{field}' must be a number",
                        severity="error",
                        path=field,
                    )
                )
            elif expected_type == "integer" and not isinstance(value, int):
                issues.append(
                    ValidationIssue(
                        message=f"Field '{field}' must be an integer",
                        severity="error",
                        path=field,
                    )
                )
            elif expected_type == "boolean" and not isinstance(value, bool):
                issues.append(
                    ValidationIssue(
                        message=f"Field '{field}' must be a boolean",
                        severity="error",
                        path=field,
                    )
                )
            elif expected_type == "array" and not isinstance(value, list):
                issues.append(
                    ValidationIssue(
                        message=f"Field '{field}' must be an array",
                        severity="error",
                        path=field,
                    )
                )
            elif expected_type == "object" and not isinstance(value, dict):
                issues.append(
                    ValidationIssue(
                        message=f"Field '{field}' must be an object",
                        severity="error",
                        path=field,
                    )
                )

        # Min/max value check for numbers
        if isinstance(value, (int, float)):
            min_value = field_rules.get("min")
            if min_value is not None and value < min_value:
                issues.append(
                    ValidationIssue(
                        message=f"Field '{field}' must be at least {min_value}",
                        severity="error",
                        path=field,
                    )
                )

            max_value = field_rules.get("max")
            if max_value is not None and value > max_value:
                issues.append(
                    ValidationIssue(
                        message=f"Field '{field}' must be at most {max_value}",
                        severity="error",
                        path=field,
                    )
                )

        # Min/max length check for strings
        if isinstance(value, str):
            min_length = field_rules.get("min_length")
            if min_length is not None and len(value) < min_length:
                issues.append(
                    ValidationIssue(
                        message=f"Field '{field}' must have at least {min_length} characters",
                        severity="error",
                        path=field,
                    )
                )

            max_length = field_rules.get("max_length")
            if max_length is not None and len(value) > max_length:
                issues.append(
                    ValidationIssue(
                        message=f"Field '{field}' must have at most {max_length} characters",
                        severity="error",
                        path=field,
                    )
                )

            # Pattern check
            pattern = field_rules.get("pattern")
            if pattern:
                import re

                if not re.match(pattern, value):
                    issues.append(
                        ValidationIssue(
                            message=f"Field '{field}' must match pattern {pattern}",
                            severity="error",
                            path=field,
                        )
                    )

            # Enum check
            enum_values = field_rules.get("enum")
            if enum_values and value not in enum_values:
                issues.append(
                    ValidationIssue(
                        message=f"Field '{field}' must be one of: {', '.join(str(v) for v in enum_values)}",
                        severity="error",
                        path=field,
                    )
                )

        # Custom validation
        custom_validation = field_rules.get("custom_validation")
        if custom_validation and callable(custom_validation):
            try:
                result = custom_validation(value)
                if isinstance(result, tuple):
                    is_valid, error_message = result
                else:
                    is_valid = bool(result)
                    error_message = None
                if not is_valid:
                    issues.append(
                        ValidationIssue(
                            message=error_message
                            or f"Field '{field}' failed custom validation",
                            severity="error",
                            path=field,
                        )
                    )
            except Exception as e:
                issues.append(
                    ValidationIssue(
                        message=f"Error in custom validation for field '{field}': {str(e)}",
                        severity="error",
                        path=field,
                    )
                )

    return ValidationResult(valid=len(issues) == 0, issues=issues)
