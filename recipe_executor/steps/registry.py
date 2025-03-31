from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# Global dictionary for mapping step type names to their implementation classes
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}


def register_step(step_type: str, step_class: Type[BaseStep]) -> None:
    """
    Register a new step implementation.

    Args:
        step_type (str): The unique name for the step type.
        step_class (Type[BaseStep]): The class implementing the step.

    Raises:
        ValueError: If the step type is already registered.
    """
    if step_type in STEP_REGISTRY:
        raise ValueError(f"Step type '{step_type}' is already registered.")
    STEP_REGISTRY[step_type] = step_class


def get_registered_step(step_type: str) -> Type[BaseStep]:
    """
    Retrieve a registered step class by its type name.

    Args:
        step_type (str): The unique name for the step type.

    Returns:
        Type[BaseStep]: The class implementing the step.

    Raises:
        ValueError: If the step type is not registered.
    """
    try:
        return STEP_REGISTRY[step_type]
    except KeyError:
        raise ValueError(f"Unknown step type '{step_type}'.")
