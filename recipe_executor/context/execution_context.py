"""Execution context for recipe execution."""

import json
import logging
import re
import string
from typing import Any, Dict, List, Optional

from recipe_executor.constants import InteractionMode, ValidationLevel, VariableScope
from recipe_executor.events.event_system import EventListener
from recipe_executor.models.events import ExecutionEvent
from recipe_executor.models.execution import StepResult
from recipe_executor.models.recipe import Recipe
from recipe_executor.models.step import RecipeStep
from recipe_executor.utils import logging as log_utils

logger = log_utils.get_logger("context")


class ExecutionContext:
    """
    Context for recipe execution, containing variables, state, and dependencies.
    Implements a scoped variable system with inheritance and isolation.
    """

    def __init__(
        self,
        variables: Optional[Dict[str, Any]] = None,
        parent: Optional["ExecutionContext"] = None,
        scope: VariableScope = VariableScope.GLOBAL,
        recipe: Optional["Recipe"] = None,
        interaction_mode: InteractionMode = InteractionMode.CRITICAL,
        validation_level: ValidationLevel = ValidationLevel.STANDARD,
    ):
        """Initialize the execution context."""
        self.variables = variables or {}
        self.parent = parent
        self.scope = scope
        self.recipe = recipe
        self._message_history = {}
        self._step_results = {}
        self._current_step = None
        self._event_listeners = []
        self.interaction_mode = interaction_mode
        self.validation_level = validation_level

        # Add the parent's event listeners
        if parent:
            for listener in parent._event_listeners:
                self._event_listeners.append(listener)

    def add_event_listener(self, listener: EventListener) -> None:
        """Add an event listener."""
        self._event_listeners.append(listener)

    def emit_event(self, event: ExecutionEvent) -> None:
        """Emit an event to all listeners."""
        for listener in self._event_listeners:
            try:
                listener.on_event(event)
            except Exception as e:
                logger.error(f"Error in event listener: {e}")

    def get_variable(self, name: str, default: Any = None) -> Any:
        """
        Get a variable from the context or its parents.

        Args:
            name: Name of the variable
            default: Default value if the variable doesn't exist

        Returns:
            Value of the variable or the default
        """
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get_variable(name, default)
        else:
            return default

    def set_variable(
        self, name: str, value: Any, scope: Optional[VariableScope] = None
    ) -> None:
        """
        Set a variable in the appropriate scope.

        Args:
            name: Name of the variable
            value: Value to set
            scope: Scope to set the variable in, or None to use the current scope
        """
        # Get the current step for logging context
        current_step = self.get_current_step()
        step_id = current_step.id if current_step else None
        
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
        
        scope_str = scope.value if scope else self.scope.value
        context_str = f" for step {step_id}" if step_id else ""
        logger.debug(f"Setting variable {name} = {display_value} (scope: {scope_str}){context_str}")
        
        if scope == VariableScope.GLOBAL or (
            not scope and self.scope == VariableScope.GLOBAL
        ):
            # Set in the root context
            if self.parent:
                self.parent.set_variable(name, value, VariableScope.GLOBAL)
            else:
                self.variables[name] = value
        else:
            # Set in the current context
            self.variables[name] = value

    def create_child_context(
        self, scope: VariableScope = VariableScope.STEP
    ) -> "ExecutionContext":
        """
        Create a child context with this context as its parent.

        Args:
            scope: Scope for the child context

        Returns:
            A new ExecutionContext with this context as its parent
        """
        return ExecutionContext(
            variables={},
            parent=self,
            scope=scope,
            recipe=self.recipe,
            interaction_mode=self.interaction_mode,
            validation_level=self.validation_level,
        )

    def get_message_history(self, step_id: str) -> List:
        """
        Get the message history for a step.

        Args:
            step_id: ID of the step

        Returns:
            List of messages in the history
        """
        if step_id in self._message_history:
            return self._message_history[step_id]
        elif self.parent:
            return self.parent.get_message_history(step_id)
        else:
            return []

    def set_message_history(self, step_id: str, messages: List) -> None:
        """
        Set the message history for a step.

        Args:
            step_id: ID of the step
            messages: List of messages to set
        """
        if self.scope == VariableScope.GLOBAL:
            self._message_history[step_id] = messages
        elif self.parent:
            self.parent.set_message_history(step_id, messages)

    def get_step_result(self, step_id: str) -> Optional["StepResult"]:
        """
        Get the result of a step.

        Args:
            step_id: ID of the step

        Returns:
            Result of the step or None if not found
        """
        if step_id in self._step_results:
            return self._step_results[step_id]
        elif self.parent:
            return self.parent.get_step_result(step_id)
        else:
            return None

    def set_step_result(self, step_id: str, result: "StepResult") -> None:
        """
        Set the result of a step.

        Args:
            step_id: ID of the step
            result: Result to set
        """
        if self.scope == VariableScope.GLOBAL:
            self._step_results[step_id] = result
        elif self.parent:
            self.parent.set_step_result(step_id, result)

    def set_current_step(self, step: Optional["RecipeStep"]) -> None:
        """
        Set the current step being executed.

        Args:
            step: Step being executed or None
        """
        self._current_step = step
        if self.parent:
            self.parent.set_current_step(step)

    def get_current_step(self) -> Optional["RecipeStep"]:
        """
        Get the current step being executed.

        Returns:
            The current step or None
        """
        if self._current_step:
            return self._current_step
        elif self.parent:
            return self.parent.get_current_step()
        else:
            return None

    def interpolate_variables(self, text: str) -> str:
        """
        Interpolate variables in a string using the template engine.
        Supports both string.Template ${var} syntax and Liquid {{ var }} syntax.

        Args:
            text: Text to interpolate

        Returns:
            Interpolated text
        """
        if not text:
            return text
            
        # First try to process with Liquid templating
        try:
            from recipe_executor.utils.liquid_renderer import render_template
            # Load the variables as a dictionary for liquid rendering
            variables_dict = {}
            
            # Special handling for variables with dots for Liquid
            dot_pattern = r'\{\{\s*([a-zA-Z0-9_]+\.[a-zA-Z0-9_.]+)\s*\}\}'
            dot_matches = re.finditer(dot_pattern, text)
            
            for match in dot_matches:
                full_var_name = match.group(1)
                parts = full_var_name.split('.')
                base_var = self.get_variable(parts[0])
                if base_var is not None:
                    variables_dict[parts[0]] = base_var
            
            # Add all direct variables
            for var_name, var_value in self.variables.items():
                variables_dict[var_name] = var_value
                
            # Add parent context variables
            if self.parent:
                parent_vars = self._get_all_parent_variables()
                for var_name, var_value in parent_vars.items():
                    if var_name not in variables_dict:  # Child vars have precedence
                        variables_dict[var_name] = var_value
            
            # Log verbose variable information for debugging
            logger.debug(f"Rendering template with {len(variables_dict)} variables")
            for key, value in variables_dict.items():
                if isinstance(value, (dict, list)):
                    try:
                        size = len(json.dumps(value))
                        logger.debug(f"Variable {key}: {type(value).__name__}, size: {size} chars")
                    except:
                        logger.debug(f"Variable {key}: {type(value).__name__}, non-serializable")
                else:
                    value_str = str(value) if value is not None else "None"
                    logger.debug(f"Variable {key}: {type(value).__name__}, value: {value_str[:50]}{'...' if len(value_str) > 50 else ''}")
                        
            # Try to render with Liquid
            result = render_template(text, variables_dict)
            logger.debug(f"Successfully rendered with Liquid templates")
            return result
        except Exception as e:
            # Fall back to string.Template for backward compatibility
            logger.debug(f"Liquid template rendering failed, falling back to string.Template: {str(e)}")
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
            
    def _get_all_parent_variables(self) -> Dict[str, Any]:
        """
        Get all variables from parent contexts.
        
        Returns:
            Dictionary of all parent variables
        """
        if not self.parent:
            return {}
            
        result = {}
        current = self.parent
        
        while current:
            for name, value in current.variables.items():
                # Don't override variables from closer parents
                if name not in result:
                    result[name] = value
            current = current.parent
            
        return result

    def evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate a condition with access to the variables.

        Args:
            condition: Condition to evaluate

        Returns:
            Result of the condition evaluation
        """
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
            "variables": {k: self.get_variable(k) for k in self.variables},
        }

        try:
            return bool(eval(condition, eval_globals, {}))
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False
