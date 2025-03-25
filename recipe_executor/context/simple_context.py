"""Simplified execution context for recipe execution."""

import json
import logging
import re
import string
from copy import deepcopy
from typing import Any, Dict, List, Optional

from recipe_executor.constants import InteractionMode, ValidationLevel
from recipe_executor.models.execution import StepResult
from recipe_executor.utils import logging as log_utils

logger = log_utils.get_logger("context")


class ExecutionContext:
    """Simple execution context with clean variable handling."""

    def __init__(
        self,
        variables: Dict[str, Any],
        recipe: Optional[Any] = None,
        validation_level: ValidationLevel = ValidationLevel.STANDARD,
        interaction_mode: InteractionMode = InteractionMode.CRITICAL,
    ):
        """Initialize with given values."""
        self._variables = variables.copy()  # Make a copy to prevent modification
        self.recipe = recipe
        self.validation_level = validation_level
        self.interaction_mode = interaction_mode
        self._step_results: Dict[str, StepResult] = {}
        self._message_history: Dict[str, List[Any]] = {}
        self._current_step = None
        
    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a variable value."""
        return self._variables.get(name, default)
        
    def with_variable(self, name: str, value: Any) -> "ExecutionContext":
        """Create a new context with an updated variable."""
        # Create a copy of the current variables
        new_variables = self._variables.copy()
        
        # Log the variable change at debug level (redacting sensitive values)
        if name.lower() in ('api_key', 'password', 'token', 'secret'):
            # Redact sensitive values in logs
            display_value = "***REDACTED***"
        elif isinstance(value, (dict, list)):
            try:
                display_value = json.dumps(value, default=str)[:100] + "..." if len(json.dumps(value, default=str)) > 100 else json.dumps(value, default=str)
            except:
                display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
        else:
            display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
            
        step_id = self._current_step.id if self._current_step else None
        context_str = f" for step {step_id}" if step_id else ""
        logger.debug(f"Setting variable {name} = {display_value}{context_str}")
        
        # Update the variable
        new_variables[name] = value
        
        # Create a new context with the updated variables
        new_context = ExecutionContext(
            variables=new_variables,
            recipe=self.recipe,
            validation_level=self.validation_level,
            interaction_mode=self.interaction_mode,
        )
        
        # Copy over step results and message history from the original context
        new_context._step_results = self._step_results.copy()
        new_context._message_history = deepcopy(self._message_history)
        new_context._current_step = self._current_step
        
        return new_context
    
    def with_variables(self, variables: Dict[str, Any]) -> "ExecutionContext":
        """Create a new context with multiple updated variables."""
        # Start with a copy of the current context
        context = self
        
        # Update each variable
        for name, value in variables.items():
            context = context.with_variable(name, value)
            
        return context
        
    def interpolate_variables(self, text: str) -> str:
        """
        Interpolate variables in a string using Liquid templates.
        
        This method supports both legacy string.Template format (${var})
        and the new liquid template format ({{ var }}).
        
        Args:
            text: The template text to interpolate
            
        Returns:
            Interpolated string with variables replaced
        """
        if not text:
            return text
            
        # Import here to avoid circular imports
        from recipe_executor.utils.liquid_renderer import render_template
        
        # Check if this is actually a liquid template (contains {{ or {%)
        if "{{" in text or "{%" in text:
            # This is a liquid template
            try:
                return render_template(text, self._variables)
            except Exception as e:
                logger.warning(f"Error rendering liquid template, falling back to string.Template: {e}")
                # Fall back to string.Template if liquid fails
        
        # Legacy string.Template support (${var} syntax)
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
                obj = self.get_variable(parts[0])
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
                value = self.get_variable(var_name)

            # Convert to string if possible
            if value is not None:
                if isinstance(value, (dict, list)):
                    substitutions[var_name] = json.dumps(value)
                else:
                    substitutions[var_name] = str(value)
            else:
                substitutions[var_name] = ""

        return template.safe_substitute(substitutions)

    def evaluate_condition(self, condition: str) -> bool:
        """Evaluate a condition with access to the variables."""
        from datetime import datetime

        if not condition:
            return True

        # Interpolate variables first
        condition = self.interpolate_variables(condition)

        # Create a safe evaluation context
        eval_globals = {
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
            "datetime": datetime,
            "re": re,
            "variables": self._variables,
        }

        try:
            return bool(eval(condition, eval_globals, {}))
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False
    
    # Message history methods
    def get_message_history(self, step_id: str) -> List[Any]:
        """Get the message history for a step."""
        return self._message_history.get(step_id, [])
    
    def set_message_history(self, step_id: str, messages: List[Any]) -> None:
        """Set the message history for a step."""
        self._message_history[step_id] = messages
    
    # Step result methods
    def get_step_result(self, step_id: str) -> Optional[StepResult]:
        """Get the result of a step."""
        return self._step_results.get(step_id)
    
    def set_step_result(self, step_id: str, result: StepResult) -> None:
        """Set the result of a step."""
        self._step_results[step_id] = result
    
    # Current step methods
    def set_current_step(self, step: Optional[Any]) -> None:
        """Set the current step being executed."""
        self._current_step = step
    
    def get_current_step(self) -> Optional[Any]:
        """Get the current step being executed."""
        return self._current_step
