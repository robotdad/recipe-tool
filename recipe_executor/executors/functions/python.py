"""Python execution executor function."""

import asyncio
from datetime import datetime
from typing import Any, Dict

from recipe_executor.constants import StepType
from recipe_executor.context.simple_context import ExecutionContext
from recipe_executor.executors.registry import register_executor
from recipe_executor.models.step import RecipeStep
from recipe_executor.utils import logging as log_utils

logger = log_utils.get_logger("python")


@register_executor(StepType.PYTHON_EXECUTE)
async def execute_python(step: RecipeStep, context: ExecutionContext) -> Any:
    """Execute a python code step."""
    if not step.python_execute:
        raise ValueError(f"Missing python_execute configuration for step {step.id}")

    config = step.python_execute
    
    # Get code from either inline code or code_file
    code = None
    if config.code:
        code = context.interpolate_variables(config.code)
    elif config.code_file:
        code_file = context.interpolate_variables(config.code_file)
        try:
            with open(code_file, "r") as f:
                code = f.read()
        except Exception as e:
            error_msg = f"Error reading code file {code_file}: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    if not code:
        raise ValueError(f"No code provided for python_execute step {step.id}")
    
    # Prepare input variables for execution
    input_vars = {}
    if config.input_variables:
        for var_name, source_var in config.input_variables.items():
            input_vars[var_name] = context.get_variable(source_var)
    
    # Execute the code
    try:
        # Create a dictionary of globals for the execution
        globals_dict = {
            "__builtins__": __builtins__,
            "asyncio": asyncio,
            "datetime": datetime,
        }
        
        # Add input variables to locals
        locals_dict = {**input_vars}
        
        # Execute the code
        logger.info(f"Executing Python code for step {step.id}")
        exec(code, globals_dict, locals_dict)
        
        # Check for a return statement
        if "return" in code:
            result = locals_dict.get("__return_value__")
            if result is None:
                # If no explicit __return_value__, look for the last expression result
                for var_name in locals_dict:
                    if var_name not in input_vars and not var_name.startswith("__"):
                        result = locals_dict[var_name]
                        break
        else:
            # If no return statement, return the entire locals_dict (excluding builtins and inputs)
            result = {k: v for k, v in locals_dict.items() 
                     if not k.startswith("__") and k not in input_vars}
            
            # If there's only one value, return it directly
            if len(result) == 1:
                result = next(iter(result.values()))
        
        return result
    except Exception as e:
        error_msg = f"Error executing Python code: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg)