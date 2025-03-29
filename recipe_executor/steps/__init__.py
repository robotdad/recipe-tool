import logging

# steps/__init__.py
from .base import STEP_REGISTRY, Step
from .generate_code import GenerateCodeStep
from .read_file import ReadFileStep
from .write_file import WriteFileStep


def get_step_instance(step_type: str, config: dict, logger: logging.Logger) -> Step:
    stype = step_type.lower()
    if stype not in STEP_REGISTRY:
        raise ValueError(f"Unknown step type: {step_type}")
    step_class, config_class = STEP_REGISTRY[stype]
    cfg = config_class.parse_obj(config)
    return step_class(cfg, logger)


__all__ = [
    "get_step_instance",
    "STEP_REGISTRY",
    "GenerateCodeStep",
    "ReadFileStep",
    "WriteFileStep",
]
