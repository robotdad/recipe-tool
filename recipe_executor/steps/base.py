import logging
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

from recipe_executor.context import Context


class StepConfig(BaseModel):
    """Base class for all step configs. Extend this in each step."""

    pass


ConfigType = TypeVar("ConfigType", bound=StepConfig)


class BaseStep(Generic[ConfigType]):
    """
    Base class for all steps. Subclasses must implement `execute(context)`.
    Each step receives a config object and a logger.
    """

    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config: ConfigType = config
        self.logger = logger or logging.getLogger("RecipeExecutor")

    def execute(self, context: Context) -> None:
        raise NotImplementedError("Each step must implement the `execute()` method.")
