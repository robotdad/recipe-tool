import logging
from typing import Any, Callable, Dict, Tuple, Type

from context import Context

# Global registry to map step type identifiers to their class and config model.
STEP_REGISTRY: Dict[str, Tuple[Type["Step"], Type[Any]]] = {}


def register_step(step_type: str, config_class: Type[Any]) -> Callable[[Type["Step"]], Type["Step"]]:
    """
    Decorator to register a Step subclass for a given step type and configuration model.

    Args:
        step_type (str): Identifier for the step (e.g., "readfile").
        config_class (Type[Any]): Pydantic model for the step's configuration.

    Returns:
        Callable: The class decorator.
    """

    def decorator(cls: Type["Step"]) -> Type["Step"]:
        STEP_REGISTRY[step_type.lower()] = (cls, config_class)
        return cls

    return decorator


class Step:
    """
    Base class for all steps.
    """

    def __init__(self, config: Any, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger

    def execute(self, context: Context) -> None:
        """
        Execute the step using the provided context.

        Args:
            context (Dict[str, Any]): Shared execution context.
        """
        raise NotImplementedError("Subclasses must implement execute().")
