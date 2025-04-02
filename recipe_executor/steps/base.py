import logging
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

from recipe_executor.context import Context


class StepConfig(BaseModel):
    """
    Base class for step configurations.

    Extend this class to create custom configuration models for steps.
    """
    pass


# Type variable for generic configuration type
ConfigType = TypeVar("ConfigType", bound=StepConfig)


class BaseStep(Generic[ConfigType], ABC):
    """
    Base abstract class for all steps in the Recipe Executor system.

    Each concrete step must inherit from this class and implement the execute method.

    Args:
        config (ConfigType): The step configuration object validated via Pydantic.
        logger (Optional[logging.Logger]): Logger instance, defaults to 'RecipeExecutor' if not provided.
    """
    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config: ConfigType = config
        self.logger: logging.Logger = logger or logging.getLogger("RecipeExecutor")
        self.logger.debug(f"Initialized {self.__class__.__name__} with config: {self.config.dict()}" if hasattr(self.config, 'dict') else f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def execute(self, context: Context) -> None:
        """
        Execute the step using the provided context.

        Args:
            context (Context): The execution context for the recipe, enabling data sharing between steps.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        # Subclasses must override this method.
        raise NotImplementedError(f"Each step must implement the execute method. {self.__class__.__name__} did not.")
