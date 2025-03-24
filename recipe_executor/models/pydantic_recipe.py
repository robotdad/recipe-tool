"""Pydantic models for recipe definition using pydantic-ai."""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class StepType(str, Enum):
    """Type of step in a recipe."""

    LLM_GENERATE = "llm_generate"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    TEMPLATE_SUBSTITUTE = "template_substitute"
    JSON_PROCESS = "json_process"
    PYTHON_EXECUTE = "python_execute"
    CONDITIONAL = "conditional"
    CHAIN = "chain"
    PARALLEL = "parallel"
    VALIDATOR = "validator"
    WAIT_FOR_INPUT = "wait_for_input"
    API_CALL = "api_call"


class ValidationLevel(str, Enum):
    """Level of validation to apply."""
    
    MINIMAL = "minimal"
    STANDARD = "standard"
    STRICT = "strict"


class InteractionMode(str, Enum):
    """How the executor interacts with users."""
    
    NONE = "none"
    CRITICAL = "critical"
    REGULAR = "regular"
    VERBOSE = "verbose"


class OutputFormat(str, Enum):
    """Format of output from LLM generation."""
    
    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    CSV = "csv"


class RecipeMetadata(BaseModel):
    """Metadata about a recipe."""
    
    name: str = Field(description="Name of the recipe")
    description: Optional[str] = Field(description="Description of what the recipe does", default=None)
    author: Optional[str] = Field(description="Author of the recipe", default=None)
    version: Optional[str] = Field(description="Version of the recipe", default=None)
    tags: Optional[List[str]] = Field(description="Tags for the recipe", default=None)


class ModelConfig(BaseModel):
    """Configuration for the LLM model to use."""
    
    name: str = Field(description="Name of the model to use")
    provider: Optional[Literal["anthropic", "openai", "google", "mistral", "ollama", "groq"]] = Field(
        description="Provider of the model", default=None
    )
    temperature: Optional[float] = Field(
        description="Temperature setting for model generation", default=None
    )
    max_tokens: Optional[int] = Field(
        description="Maximum tokens to generate", default=None
    )


class LLMGenerateConfig(BaseModel):
    """Configuration for LLM generation step."""
    
    prompt: str = Field(description="Prompt to send to the LLM")
    model: Optional[str] = Field(description="Model to use for this step, overrides recipe default", default=None)
    provider: Optional[Literal["anthropic", "openai", "google", "mistral", "ollama", "groq"]] = Field(
        description="Provider to use for this step, overrides recipe default", default=None
    )
    temperature: Optional[float] = Field(description="Temperature for generation", default=None)
    max_tokens: Optional[int] = Field(description="Maximum tokens to generate", default=None)
    output_format: Optional[OutputFormat] = Field(description="Expected format of output", default=None)
    output_variable: str = Field(description="Variable to store the result in")
    validation_schema: Optional[Dict[str, Any]] = Field(
        description="JSON schema for validating output", default=None
    )


class FileReadConfig(BaseModel):
    """Configuration for file read step."""
    
    path: str = Field(description="Path to the file to read")
    output_variable: str = Field(description="Variable to store the result in")
    binary: Optional[bool] = Field(description="Whether to read as binary", default=False)


class FileWriteConfig(BaseModel):
    """Configuration for file write step."""
    
    path: str = Field(description="Path to write the file to")
    content: Union[str, Dict[str, Any]] = Field(description="Content to write to the file")
    mode: Optional[str] = Field(description="File mode (e.g., 'w', 'a')", default="w")
    binary: Optional[bool] = Field(description="Whether to write as binary", default=False)


class TemplateSubstituteConfig(BaseModel):
    """Configuration for template substitution step."""
    
    template: str = Field(description="Template string to substitute")
    output_variable: str = Field(description="Variable to store the result in")
    variables: Optional[Dict[str, Any]] = Field(
        description="Variables to use for substitution, uses recipe context if not provided", default=None
    )


class JsonProcessConfig(BaseModel):
    """Configuration for JSON processing step."""
    
    data: Union[str, Dict[str, Any]] = Field(description="JSON data to process, or variable name containing it")
    operations: List[Dict[str, Any]] = Field(description="Operations to perform on the JSON")
    output_variable: str = Field(description="Variable to store the result in")


class PythonExecuteConfig(BaseModel):
    """Configuration for Python execution step."""
    
    code: str = Field(description="Python code to execute")
    output_variable: Optional[str] = Field(description="Variable to store the result in", default=None)
    timeout: Optional[int] = Field(description="Timeout in seconds", default=30)


class ConditionalConfig(BaseModel):
    """Configuration for conditional step."""
    
    condition: str = Field(description="Condition to evaluate")
    if_true: str = Field(description="Step to execute if condition is true")
    if_false: Optional[str] = Field(description="Step to execute if condition is false", default=None)


class ChainConfig(BaseModel):
    """Configuration for chain step."""
    
    steps: List[str] = Field(description="Steps to execute in sequence")


class ParallelConfig(BaseModel):
    """Configuration for parallel step."""
    
    steps: List[str] = Field(description="Steps to execute in parallel")
    output_variable: Optional[str] = Field(description="Variable to store the results in", default=None)


class ValidatorConfig(BaseModel):
    """Configuration for validator step."""
    
    data: Union[str, Dict[str, Any]] = Field(description="Data to validate, or variable name containing it")
    validation_schema: Dict[str, Any] = Field(description="JSON schema to validate against")
    output_variable: Optional[str] = Field(description="Variable to store the validation result in", default=None)


class WaitForInputConfig(BaseModel):
    """Configuration for waiting for user input."""
    
    prompt: str = Field(description="Prompt to display to the user")
    output_variable: str = Field(description="Variable to store the input in")
    default: Optional[str] = Field(description="Default value if user enters nothing", default=None)
    choices: Optional[List[str]] = Field(description="Valid choices for input", default=None)
    validation: Optional[Dict[str, Any]] = Field(description="Validation rules for input", default=None)


class ApiCallConfig(BaseModel):
    """Configuration for API call step."""
    
    url: str = Field(description="URL to call")
    method: str = Field(description="HTTP method", default="GET")
    headers: Optional[Dict[str, str]] = Field(description="HTTP headers", default=None)
    params: Optional[Dict[str, Any]] = Field(description="Query parameters", default=None)
    data: Optional[Union[Dict[str, Any], str]] = Field(description="Request body", default=None)
    auth: Optional[Dict[str, str]] = Field(description="Authentication details", default=None)
    output_variable: str = Field(description="Variable to store the response in")
    timeout: Optional[int] = Field(description="Timeout in seconds", default=30)


class RecipeStep(BaseModel):
    """A step in a recipe."""
    
    id: str = Field(description="Unique identifier for the step")
    name: Optional[str] = Field(description="Human-readable name for the step", default=None)
    type: StepType = Field(description="Type of step")
    description: Optional[str] = Field(description="Description of what this step does", default=None)
    condition: Optional[str] = Field(description="Condition that determines if this step runs", default=None)
    critical: Optional[bool] = Field(description="Whether failure of this step should abort the recipe", default=False)
    depends_on: Optional[List[str]] = Field(description="Steps that must complete before this one runs", default=None)
    continue_on_error: Optional[bool] = Field(description="Whether to continue execution if this step fails", default=False)
    retry_count: Optional[int] = Field(description="Number of times to retry this step if it fails", default=0)
    retry_delay: Optional[int] = Field(description="Delay in seconds between retries", default=1)
    validation_level: Optional[ValidationLevel] = Field(
        description="Validation level for this step", default=None
    )
    
    # Step-specific configurations
    llm_generate: Optional[LLMGenerateConfig] = None
    file_read: Optional[FileReadConfig] = None
    file_write: Optional[FileWriteConfig] = None
    template_substitute: Optional[TemplateSubstituteConfig] = None
    json_process: Optional[JsonProcessConfig] = None
    python_execute: Optional[PythonExecuteConfig] = None
    conditional: Optional[ConditionalConfig] = None
    chain: Optional[ChainConfig] = None
    parallel: Optional[ParallelConfig] = None
    validator: Optional[ValidatorConfig] = None
    wait_for_input: Optional[WaitForInputConfig] = None
    api_call: Optional[ApiCallConfig] = None


class Recipe(BaseModel):
    """A complete recipe for the LLM to execute."""
    
    metadata: RecipeMetadata = Field(description="Metadata about the recipe")
    model: Optional[ModelConfig] = Field(description="Global model configuration for the recipe", default=None)
    variables: Dict[str, Any] = Field(description="Initial variables for the recipe", default_factory=dict)
    steps: List[RecipeStep] = Field(description="Steps to execute in the recipe")
    validation_level: ValidationLevel = Field(
        description="Default validation level for all steps",
        default=ValidationLevel.STANDARD,
    )
    interaction_mode: InteractionMode = Field(
        description="How the executor interacts with users",
        default=InteractionMode.CRITICAL,
    )
    max_retries: int = Field(description="Default maximum retries for steps", default=3)
    timeout: Optional[int] = Field(description="Overall timeout for the entire recipe in seconds", default=None)