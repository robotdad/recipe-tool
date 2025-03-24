"""Template substitution executor implementation."""

import logging
import re
import string
from typing import Any

from recipe_executor.context.execution_context import ExecutionContext
from recipe_executor.models.step import RecipeStep
from recipe_executor.models.validation import ValidationIssue, ValidationResult

logger = logging.getLogger("recipe-executor")


class TemplateSubstituteExecutor:
    """Executor for template substitution steps."""

    async def execute(self, step: RecipeStep, context: ExecutionContext) -> str:
        """
        Execute a template substitution step.

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            Substituted template
        """
        if not step.template_substitute:
            raise ValueError(
                f"Missing template_substitute configuration for step {step.id}"
            )

        config = step.template_substitute

        # Get the template content
        if config.template_file:
            template_file = context.interpolate_variables(config.template_file)
            try:
                with open(template_file, "r") as f:
                    template_content = f.read()
            except Exception as e:
                logger.error(f"Error reading template file {template_file}: {e}")
                if not step.continue_on_error:
                    raise
                return ""
        else:
            template_content = config.template

        # Create a Template object
        template = string.Template(template_content)

        # Get variables to substitute
        variables = {}
        for var_name, var_source in config.variables.items():
            var_source = context.interpolate_variables(var_source)
            var_value = context.get_variable(var_source)
            if var_value is not None:
                variables[var_name] = var_value
            else:
                variables[var_name] = var_source

        # Convert all variables to strings for interpolation
        str_variables = {
            k: str(v) if v is not None else "" for k, v in variables.items()
        }

        # Perform substitution
        result = template.safe_substitute(str_variables)

        return result

    async def validate_result(
        self, step: RecipeStep, result: Any, context: ExecutionContext
    ) -> ValidationResult:
        """
        Validate the result of a template substitution step.

        Args:
            step: Step to validate
            result: Result to validate
            context: Execution context

        Returns:
            Validation result
        """
        if not step.template_substitute:
            return ValidationResult(valid=True, issues=[])

        # Check for unresolved variables
        unresolved_vars = re.findall(r"\$\{([^}]*)\}", result)

        if unresolved_vars:
            return ValidationResult(
                valid=False,
                issues=[
                    ValidationIssue(
                        message=f"Unresolved variable(s) in template: {', '.join(unresolved_vars)}",
                        severity="warning",
                    )
                ],
            )

        return ValidationResult(valid=True, issues=[])
