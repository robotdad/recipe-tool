import logging
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

from recipe_executor.context import Context


class StepConfig(BaseModel):
    """
    Base class for all step configurations. Extend this class to add custom configuration fields.
    """

    pass


# Type variable for generic configuration types, bound to StepConfig
ConfigType = TypeVar("ConfigType", bound=StepConfig)


class BaseStep(ABC, Generic[ConfigType]):
    """
    Abstract base class for all steps. Subclasses should implement the execute method.

    Attributes:
        config (ConfigType): The configuration for the step, validated via Pydantic.
        logger (logging.Logger): Logger instance for logging messages during execution.
    """

    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config = config
        self.logger = logger or logging.getLogger("RecipeExecutor")
        if not self.logger.handlers:
            # Basic handler setup if no handlers are present, ensuring logging output
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    @abstractmethod
    def execute(self, context: Context) -> None:
        """
        Execute the step using a provided context.

        Args:
            context (Context): Shared context object carrying data between steps.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement the execute method.")
