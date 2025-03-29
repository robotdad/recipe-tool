from abc import ABC, abstractmethod

# Global registry for steps
STEP_REGISTRY = {}


def register_step(step_type: str):
    def decorator(cls):
        STEP_REGISTRY[step_type] = cls
        return cls
    return decorator


class Step(ABC):
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    @abstractmethod
    def execute(self, context):
        pass
