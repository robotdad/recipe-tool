"""Implementations of step executors."""

from recipe_executor.constants import StepType
from recipe_executor.executors.implementations.api import ApiCallExecutor
from recipe_executor.executors.implementations.chain import ChainExecutor
from recipe_executor.executors.implementations.conditional import ConditionalExecutor
from recipe_executor.executors.implementations.file import (
    FileReadExecutor,
    FileWriteExecutor,
)
from recipe_executor.executors.implementations.input import WaitForInputExecutor
from recipe_executor.executors.implementations.json import JsonProcessExecutor
from recipe_executor.executors.implementations.llm import LLMGenerateExecutor
from recipe_executor.executors.implementations.parallel import ParallelExecutor
from recipe_executor.executors.implementations.python import PythonExecuteExecutor
from recipe_executor.executors.implementations.template import (
    TemplateSubstituteExecutor,
)
from recipe_executor.executors.implementations.validator import ValidatorExecutor


def get_all_executors(cache_dir=None):
    """Get all step executors."""
    return {
        StepType.LLM_GENERATE: LLMGenerateExecutor(cache_dir=cache_dir),
        StepType.FILE_READ: FileReadExecutor(),
        StepType.FILE_WRITE: FileWriteExecutor(),
        StepType.TEMPLATE_SUBSTITUTE: TemplateSubstituteExecutor(),
        StepType.JSON_PROCESS: JsonProcessExecutor(),
        StepType.PYTHON_EXECUTE: PythonExecuteExecutor(),
        StepType.CONDITIONAL: ConditionalExecutor(),
        StepType.CHAIN: ChainExecutor(),
        StepType.PARALLEL: ParallelExecutor(),
        StepType.VALIDATOR: ValidatorExecutor(),
        StepType.WAIT_FOR_INPUT: WaitForInputExecutor(),
        StepType.API_CALL: ApiCallExecutor(),
    }


__all__ = [
    "LLMGenerateExecutor",
    "FileReadExecutor",
    "FileWriteExecutor",
    "TemplateSubstituteExecutor",
    "JsonProcessExecutor",
    "PythonExecuteExecutor",
    "ConditionalExecutor",
    "ChainExecutor",
    "ParallelExecutor",
    "ValidatorExecutor",
    "WaitForInputExecutor",
    "ApiCallExecutor",
    "get_all_executors",
]
