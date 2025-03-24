"""JSON processing executor implementation."""

import json
import logging
import re
from typing import Any

from recipe_executor.context.execution_context import ExecutionContext
from recipe_executor.models.step import RecipeStep
from recipe_executor.models.validation import ValidationIssue, ValidationResult

logger = logging.getLogger("recipe-executor")


class JsonProcessExecutor:
    """Executor for JSON processing steps."""

    async def execute(self, step: RecipeStep, context: ExecutionContext) -> Any:
        """
        Execute a JSON process step.

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            Processed JSON data (can be dict, list, string, number, or None)
        """
        if not step.json_process:
            raise ValueError(f"Missing json_process configuration for step {step.id}")

        config = step.json_process

        input_var = context.get_variable(config.input_variable)
        if input_var is None:
            raise ValueError(f"Input variable {config.input_variable} not found")

        # If input is a string, try to parse it as JSON
        if isinstance(input_var, str):
            try:
                input_data = json.loads(input_var)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse input as JSON: {input_var[:100]}...")
                input_data = {"text": input_var}
        else:
            input_data = input_var

        result = input_data

        # Process each operation in sequence
        for op in config.operations:
            op_type = op.get("type")

            if op_type == "extract":
                # Extract a value from the JSON using a path
                path = op.get("path", "")
                default = op.get("default")
                keys = path.split(".")

                value = result
                for key in keys:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    elif (
                        isinstance(value, list)
                        and key.isdigit()
                        and int(key) < len(value)
                    ):
                        value = value[int(key)]
                    else:
                        value = default
                        break

                result = value
            elif op_type == "filter":
                # Filter an array of objects based on a condition
                if not isinstance(result, list):
                    logger.warning(
                        f"Filter operation requires a list, got {type(result)}"
                    )
                    continue

                field = op.get("field", "")
                value = op.get("value")
                operator = op.get("operator", "eq")

                filtered = []
                for item in result:
                    if not isinstance(item, dict):
                        continue

                    item_value = item.get(field)

                    if (
                        operator == "gt"
                        and item_value is not None
                        and value is not None
                        and item_value > value
                    ):
                        filtered.append(item)
                    elif (
                        operator == "lt"
                        and item_value is not None
                        and value is not None
                        and item_value < value
                    ):
                        filtered.append(item)
                    elif (
                        operator == "contains"
                        and item_value is not None
                        and value is not None
                        and isinstance(item_value, (str, list, tuple, dict))
                        and value in item_value
                    ):
                        filtered.append(item)
                    elif (
                        operator == "startswith"
                        and isinstance(item_value, str)
                        and value is not None
                        and item_value.startswith(str(value))
                    ):
                        filtered.append(item)
                    elif (
                        operator == "endswith"
                        and isinstance(item_value, str)
                        and value is not None
                        and item_value.endswith(str(value))
                    ):
                        filtered.append(item)
                    elif (
                        operator == "in"
                        and item_value is not None
                        and value is not None
                        and hasattr(value, "__contains__")
                        and item_value in value
                    ):
                        filtered.append(item)

                result = filtered
            elif op_type == "map":
                # Map an array of objects to a new array
                if not isinstance(result, list):
                    logger.warning(f"Map operation requires a list, got {type(result)}")
                    continue

                template = op.get("template", {})

                mapped = []
                for item in result:
                    if not isinstance(item, dict):
                        continue

                    new_item = {}
                    for new_key, source_path in template.items():
                        keys = source_path.split(".")
                        value = item
                        for key in keys:
                            if isinstance(value, dict) and key in value:
                                value = value[key]
                            else:
                                value = None
                                break

                        new_item[new_key] = value

                    mapped.append(new_item)

                result = mapped
            elif op_type == "merge":
                # Merge multiple objects
                other_var = op.get("with")
                if other_var in context.variables:
                    other_data = context.get_variable(other_var)
                    if isinstance(other_data, dict) and isinstance(result, dict):
                        result = {**result, **other_data}
                    elif isinstance(other_data, list) and isinstance(result, list):
                        result.extend(other_data)
            elif op_type == "sort":
                # Sort an array
                if not isinstance(result, list):
                    logger.warning(
                        f"Sort operation requires a list, got {type(result)}"
                    )
                    continue

                field = op.get("field")
                reverse = op.get("reverse", False)

                if field:
                    # Sort by field with a safe key function
                    def safe_sort_key(x):
                        if isinstance(x, dict):
                            val = x.get(field)
                            # Return a default comparable value if None or not comparable
                            if val is None:
                                return ""
                            return val
                        return x

                    result = sorted(
                        result,
                        key=safe_sort_key,
                        reverse=reverse,
                    )
                else:
                    # Sort directly with None handling
                    # Create a list of (index, value) pairs where None values are replaced
                    # with a default value for sorting purposes
                    indexed_result = []
                    for i, value in enumerate(result):
                        if value is None:
                            # Use (index, empty string) for None values to keep them together
                            indexed_result.append((i, ""))
                        else:
                            indexed_result.append((i, value))

                    # Sort by the value
                    sorted_pairs = sorted(
                        indexed_result, key=lambda pair: pair[1], reverse=reverse
                    )

                    # Rebuild the result list from the original values by index
                    result = [result[i] for i, _ in sorted_pairs]

            elif op_type == "group":
                # Group by field
                if not isinstance(result, list):
                    logger.warning(
                        f"Group operation requires a list, got {type(result)}"
                    )
                    continue

                field = op.get("field")
                if not field:
                    logger.warning("Group operation requires a field")
                    continue

                grouped = {}
                for item in result:
                    if not isinstance(item, dict):
                        continue

                    key = item.get(field)
                    if key not in grouped:
                        grouped[key] = []

                    grouped[key].append(item)

                result = grouped
            elif op_type == "aggregate":
                # Aggregate values
                if not isinstance(result, list):
                    logger.warning(
                        f"Aggregate operation requires a list, got {type(result)}"
                    )
                    continue

                field = op.get("field")
                function = op.get("function", "sum")

                if not field:
                    logger.warning("Aggregate operation requires a field")
                    continue

                values = []
                for item in result:
                    if not isinstance(item, dict):
                        continue

                    if field in item and item[field] is not None:
                        values.append(item[field])

                if function == "sum":
                    result = sum(values) if values else 0
                elif function == "avg":
                    result = sum(values) / len(values) if values else 0
                elif function == "min":
                    result = min(values) if values else None
                elif function == "max":
                    result = max(values) if values else None
                elif function == "count":
                    result = len(values)
            elif op_type == "custom":
                # Custom Python code to process the JSON
                code = op.get("code", "")
                if code:
                    from datetime import datetime

                    eval_globals = {
                        "json_data": result,
                        "json": json,
                        "datetime": datetime,
                        "re": re,
                    }

                    try:
                        result = eval(code, eval_globals, {})
                    except Exception as e:
                        logger.error(f"Error evaluating custom code: {e}")
                        if not step.continue_on_error:
                            raise

        return result

    async def validate_result(
        self, step: RecipeStep, result: Any, context: ExecutionContext
    ) -> ValidationResult:
        """
        Validate the result of a JSON process step.

        Args:
            step: Step to validate
            result: Result to validate
            context: Execution context

        Returns:
            Validation result
        """
        if not step.json_process:
            return ValidationResult(valid=True, issues=[])

        config = step.json_process

        # Check against validation schema if provided
        if config.validation_schema:
            try:
                from jsonschema import (
                    ValidationError as JsonSchemaValidationError,
                )
                from jsonschema import (
                    validate,
                )

                try:
                    validate(instance=result, schema=config.validation_schema)
                    return ValidationResult(valid=True, issues=[])
                except JsonSchemaValidationError as e:
                    return ValidationResult(
                        valid=False,
                        issues=[
                            ValidationIssue(
                                message=f"JSON schema validation failed: {e.message}",
                                severity="error",
                                path=".".join(str(p) for p in e.path)
                                if e.path
                                else None,
                            )
                        ],
                    )
            except ImportError:
                logger.warning(
                    "jsonschema package not installed, skipping schema validation"
                )

        return ValidationResult(valid=True, issues=[])
