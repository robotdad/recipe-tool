from typing import Any, Union, Literal
import logging

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol
from recipe_executor.utils.templates import render_template


class SetContextConfig(StepConfig):
    """
    Config for SetContextStep.

    Fields:
        key: Name of the artifact in the Context.
        value: String, list, dict or Liquid template string rendered against
               the current context.
        if_exists: Strategy when the key already exists:
                   • "overwrite" (default) – replace the existing value
                   • "merge" – combine the existing and new values
    """
    key: str
    value: Union[str, list, dict]
    if_exists: Literal["overwrite", "merge"] = "overwrite"


class SetContextStep(BaseStep[SetContextConfig]):
    """
    Step to set or update an artifact in the execution context.
    """
    def __init__(self, logger: logging.Logger, config: dict) -> None:
        super().__init__(logger, SetContextConfig.model_validate(config))

    async def execute(self, context: ContextProtocol) -> None:
        key = self.config.key
        raw_value = self.config.value
        existed = key in context

        # Render template if the provided value is a string
        if isinstance(raw_value, str):
            value: Any = render_template(raw_value, context)
        else:
            value = raw_value

        strategy = self.config.if_exists
        if strategy == "overwrite":
            context[key] = value
        elif strategy == "merge":
            if existed:
                old = context[key]
                merged = self._merge(old, value)
                context[key] = merged
            else:
                context[key] = value
        else:
            raise ValueError(f"Unknown if_exists strategy: '{strategy}'")

        self.logger.info(
            f"SetContextStep: key='{key}', strategy='{strategy}', existed={existed}"
        )

    def _merge(self, old: Any, new: Any) -> Any:
        """
        Shallow merge helper for merging existing and new values.
        """
        # String + string => concatenate
        if isinstance(old, str) and isinstance(new, str):
            return old + new

        # List + list or item => append
        if isinstance(old, list):
            if isinstance(new, list):
                return old + new  # type: ignore
            return old + [new]

        # Dict + dict => shallow merge
        if isinstance(old, dict) and isinstance(new, dict):
            merged = old.copy()
            merged.update(new)
            return merged

        # Fallback for mismatched types
        return [old, new]
