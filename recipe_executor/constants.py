"""Constants and enums for the Recipe Executor system."""

from enum import Enum


class StepType(str, Enum):
    """Types of recipe steps that can be executed."""

    LLM_GENERATE = "llm_generate"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    TEMPLATE_SUBSTITUTE = "template_substitute"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    JSON_PROCESS = "json_process"
    PYTHON_EXECUTE = "python_execute"
    CHAIN = "chain"
    VALIDATOR = "validator"
    WAIT_FOR_INPUT = "wait_for_input"
    API_CALL = "api_call"


class ExecutionStatus(str, Enum):
    """Status of the recipe execution."""

    NOT_STARTED = "not_started"
    PLANNING = "planning"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    """Status of a step execution."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ValidationLevel(str, Enum):
    """Levels of validation strictness."""

    MINIMAL = "minimal"  # Basic type checking
    STANDARD = "standard"  # Schema validation
    STRICT = "strict"  # Comprehensive validation with business rules


class InteractionMode(str, Enum):
    """How the executor interacts with users."""

    NONE = "none"  # No interaction, fails on error
    CRITICAL = "critical"  # Only interact on critical errors
    REGULAR = "regular"  # Interact at key decision points
    VERBOSE = "verbose"  # Interact frequently for guidance


class OutputFormat(str, Enum):
    """Output formats that can be used for LLM responses."""

    TEXT = "text"
    JSON = "json"
    STRUCTURED = "structured"
    FILES = "files"


class VariableScope(str, Enum):
    """Scope for variables in the recipe."""

    GLOBAL = "global"  # Available throughout the recipe
    STEP = "step"  # Only available within the step
    CHAIN = "chain"  # Available within a chain of steps
