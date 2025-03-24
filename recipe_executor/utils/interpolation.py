"""Variable interpolation utilities for Recipe Executor."""

import json
import logging
import re
import string
from typing import Any, Dict, Optional

logger = logging.getLogger("recipe-executor")


def interpolate_variables(text: str, variables: Dict[str, Any]) -> str:
    """
    Interpolate variables in a string using the template engine.

    Args:
        text: Text to interpolate
        variables: Dictionary of variables to interpolate

    Returns:
        Interpolated text
    """
    if not text:
        return text

    template = string.Template(text)

    # Get all potential variables from the template
    var_pattern = r"\$\{([^}]*)\}|\$([a-zA-Z0-9_]+)"
    var_matches = re.finditer(var_pattern, text)
    var_names = [match.group(1) or match.group(2) for match in var_matches]

    # Prepare substitutions
    substitutions = {}
    for var_name in var_names:
        # Check for nested references
        if "." in var_name:
            parts = var_name.split(".")
            obj = variables.get(parts[0])
            value = obj
            for part in parts[1:]:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                elif hasattr(value, part):
                    value = getattr(value, part)
                else:
                    value = None
                    break
        else:
            # Direct variable reference
            value = variables.get(var_name)

        # Convert to string if possible
        if value is not None:
            if isinstance(value, (dict, list)):
                substitutions[var_name] = json.dumps(value)
            else:
                substitutions[var_name] = str(value)
        else:
            substitutions[var_name] = ""

    return template.safe_substitute(substitutions)


def evaluate_expression(
    expression: str, variables: Dict[str, Any], default: Optional[Any] = None
) -> Any:
    """
    Evaluate a Python expression with variables.

    Args:
        expression: Expression to evaluate
        variables: Dictionary of variables to use in evaluation
        default: Default value if evaluation fails

    Returns:
        Result of evaluation or default value
    """
    # First interpolate any string variables
    interpolated_expr = interpolate_variables(expression, variables)

    # Create safe execution environment
    import re
    from datetime import datetime

    eval_globals = {
        # Python builtins
        "len": len,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
        "set": set,
        "sum": sum,
        "min": min,
        "max": max,
        "all": all,
        "any": any,
        "enumerate": enumerate,
        "zip": zip,
        # External modules
        "datetime": datetime,
        "re": re,
        # Variables
        "variables": variables,
    }

    try:
        return eval(interpolated_expr, eval_globals, {})
    except Exception as e:
        logger.error(f"Error evaluating expression '{expression}': {e}")
        return default
