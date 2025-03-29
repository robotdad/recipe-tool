from .base import STEP_REGISTRY, Step
from .read_file import ReadFileStep
from .generate_code import GenerateCodeStep
from .write_file import WriteFileStep


def get_step_instance(step_type: str, config: dict, logger):
    if step_type not in STEP_REGISTRY:
        raise ValueError(f'Unknown step type: {step_type}')
    step_cls = STEP_REGISTRY[step_type]
    return step_cls(config, logger)
