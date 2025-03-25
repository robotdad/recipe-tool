"""Template substitution executor function."""

import logging
from typing import Any, Dict

from recipe_executor.constants import StepType
from recipe_executor.context.simple_context import ExecutionContext
from recipe_executor.executors.registry import register_executor
from recipe_executor.models.step import RecipeStep
from recipe_executor.utils import logging as log_utils
from recipe_executor.utils.liquid_renderer import render_template

logger = log_utils.get_logger("template")


@register_executor(StepType.TEMPLATE_SUBSTITUTE)
async def execute_template_substitute(step: RecipeStep, context: ExecutionContext) -> str:
    """
    Execute a template substitution step with Liquid template engine.
    
    Args:
        step: Step to execute
        context: Execution context
    
    Returns:
        Substituted template
    """
    if not step.template_substitute:
        raise ValueError(f"Missing template_substitute configuration for step {step.id}")

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

    # Get variables to substitute
    variables = {}
    if hasattr(config, "variables") and config.variables:
        for var_name, var_source in config.variables.items():
            var_source = context.interpolate_variables(var_source)
            var_value = context.get_variable(var_source)
            if var_value is not None:
                variables[var_name] = var_value
            else:
                variables[var_name] = var_source
    else:
        # If no specific variables mapping provided, use all context variables
        variables = context._variables.copy()

    # Render the template
    try:
        # First try with the new Liquid template engine
        result = render_template(template_content, variables)
        logger.debug(f"Template substitution for step {step.id} completed using Liquid templates")
        return result
    except Exception as e:
        logger.warning(f"Error rendering with Liquid templates, falling back to simple substitution: {e}")
        # Fall back to interpolate_variables for backward compatibility
        result = context.interpolate_variables(template_content)
        return result