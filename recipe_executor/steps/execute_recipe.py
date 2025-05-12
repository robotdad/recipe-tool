import os
import json
from typing import Any, Dict

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol
from recipe_executor.utils.templates import render_template

__all__ = ["ExecuteRecipeConfig", "ExecuteRecipeStep"]


def _render_override(value: Any, context: ContextProtocol) -> Any:
    """
    Recursively render and parse override values.

    - Strings are template-rendered, then if the result is valid JSON (dict or list), parsed into Python objects.
    - Lists and dicts are processed recursively.
    - Other types are returned as-is.
    """
    if isinstance(value, str):
        rendered = render_template(value, context)
        # Attempt to parse JSON if it represents an object or array
        try:
            parsed = json.loads(rendered)
            if isinstance(parsed, (dict, list)):
                return parsed
        except json.JSONDecodeError:
            pass
        return rendered
    if isinstance(value, list):  # type: ignore[type-arg]
        return [_render_override(item, context) for item in value]
    if isinstance(value, dict):  # type: ignore[type-arg]
        return {key: _render_override(val, context) for key, val in value.items()}
    return value


class ExecuteRecipeConfig(StepConfig):
    """Config for ExecuteRecipeStep.

    Fields:
        recipe_path: Path to the sub-recipe to execute (templateable).
        context_overrides: Optional values to override in the context.
    """
    recipe_path: str
    context_overrides: Dict[str, Any] = {}


class ExecuteRecipeStep(BaseStep[ExecuteRecipeConfig]):
    """Step to execute a sub-recipe with shared context and optional overrides."""

    def __init__(
        self,
        logger,  # type: ignore[valid-type]
        config: Dict[str, Any]
    ) -> None:
        validated: ExecuteRecipeConfig = ExecuteRecipeConfig.model_validate(config)
        super().__init__(logger, validated)

    async def execute(self, context: ContextProtocol) -> None:
        """
        Execute a sub-recipe located at the rendered recipe_path.

        Applies context_overrides before execution, shares the same context,
        and logs progress.
        """
        # Render and validate recipe path
        rendered_path = render_template(self.config.recipe_path, context)
        if not os.path.isfile(rendered_path):
            raise FileNotFoundError(f"Sub-recipe file not found: {rendered_path}")

        # Apply context overrides with templating and JSON parsing
        for key, override_value in self.config.context_overrides.items():
            rendered_value = _render_override(override_value, context)
            context[key] = rendered_value

        try:
            # Import here to avoid circular dependencies
            from recipe_executor.executor import Executor

            self.logger.info(f"Starting sub-recipe execution: {rendered_path}")
            executor = Executor(self.logger)
            await executor.execute(rendered_path, context)
            self.logger.info(f"Completed sub-recipe execution: {rendered_path}")
        except Exception as exc:
            # Log and propagate with context
            self.logger.error(f"Error executing sub-recipe '{rendered_path}': {exc}")
            raise RuntimeError(
                f"Failed to execute sub-recipe '{rendered_path}': {exc}"
            ) from exc
