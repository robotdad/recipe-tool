from typing import Any, Dict, Tuple, Type

# Global registry to map step type identifiers to their class and config model.
STEP_REGISTRY: Dict[str, Tuple[Type["Step"], Type]] = {}


def register_step(step_type: str, config_class: Type) -> callable:
    """
    Decorator to register a Step subclass for a given step type and configuration model.

    Args:
        step_type (str): Identifier for the step (e.g., "readfile").
        config_class (Type): Pydantic model for the step's configuration.

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

    def execute(self, context: Dict[str, Any]) -> None:
        """
        Execute the step using the provided context.

        Args:
            context (Dict[str, Any]): Shared execution context.
        """
        raise NotImplementedError("Subclasses must implement execute().")
