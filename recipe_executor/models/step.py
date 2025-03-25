"""Step model for recipe execution."""

from typing import List, Optional

from pydantic import BaseModel, Field, model_validator

from recipe_executor.constants import StepType, ValidationLevel
from recipe_executor.models.config.api import ApiCallConfig
from recipe_executor.models.config.chain import ChainConfig
from recipe_executor.models.config.conditional import ConditionalConfig
from recipe_executor.models.config.file import FileInputConfig, FileOutputConfig
from recipe_executor.models.config.input import WaitForInputConfig
from recipe_executor.models.config.json import JsonProcessConfig
from recipe_executor.models.config.llm import LLMGenerateConfig
from recipe_executor.models.config.parallel import ParallelConfig
from recipe_executor.models.config.python import PythonExecuteConfig
from recipe_executor.models.config.template import TemplateSubstituteConfig
from recipe_executor.models.config.validator import ValidatorConfig


class RecipeStep(BaseModel):
    """A step in a recipe."""

    id: str = Field(description="Unique identifier for the step")
    name: Optional[str] = Field(
        description="Human-readable name for the step", default=None
    )
    description: Optional[str] = Field(
        description="Description of what the step does", default=None
    )
    type: StepType = Field(description="Type of step to execute")

    # Step-specific configurations
    llm_generate: Optional[LLMGenerateConfig] = Field(
        description="Configuration for LLM generation", default=None
    )
    file_read: Optional[FileInputConfig] = Field(
        description="Configuration for file reading", default=None
    )
    file_write: Optional[FileOutputConfig] = Field(
        description="Configuration for file writing", default=None
    )
    template_substitute: Optional[TemplateSubstituteConfig] = Field(
        description="Configuration for template substitution", default=None
    )
    json_process: Optional[JsonProcessConfig] = Field(
        description="Configuration for JSON processing", default=None
    )
    python_execute: Optional[PythonExecuteConfig] = Field(
        description="Configuration for Python execution", default=None
    )
    conditional: Optional[ConditionalConfig] = Field(
        description="Configuration for conditional execution", default=None
    )
    chain: Optional[ChainConfig] = Field(
        description="Configuration for chaining steps", default=None
    )
    parallel: Optional[ParallelConfig] = Field(
        description="Configuration for parallel execution", default=None
    )
    validator: Optional[ValidatorConfig] = Field(
        description="Configuration for validation", default=None
    )
    wait_for_input: Optional[WaitForInputConfig] = Field(
        description="Configuration for waiting for user input", default=None
    )
    api_call: Optional[ApiCallConfig] = Field(
        description="Configuration for making API calls", default=None
    )

    # Execution control
    condition: Optional[str] = Field(
        description="Condition to determine if this step should run", default=None
    )
    continue_on_error: bool = Field(
        description="Whether to continue execution if this step fails", default=False
    )
    retry_count: int = Field(
        description="Number of times to retry the step if it fails", default=0
    )
    retry_delay: int = Field(description="Delay in seconds between retries", default=1)
    timeout: Optional[int] = Field(
        description="Timeout in seconds for this step", default=None
    )
    depends_on: Optional[List[str]] = Field(
        description="IDs of steps that must complete before this step", default=None
    )
    critical: bool = Field(
        description="Whether this step is critical for the recipe", default=False
    )
    validation_level: ValidationLevel = Field(
        description="Level of validation to apply", default=ValidationLevel.STANDARD
    )

    # For validation
    @model_validator(mode="after")
    def validate_step_config(self) -> "RecipeStep":
        """Validate that the step has the correct configuration for its type."""
        # Map step types to their configuration field names
        step_config_fields = {
            StepType.LLM_GENERATE: "llm_generate",
            StepType.FILE_READ: "file_read",
            StepType.FILE_WRITE: "file_write",
            StepType.TEMPLATE_SUBSTITUTE: "template_substitute",
            StepType.JSON_PROCESS: "json_process",
            StepType.PYTHON_EXECUTE: "python_execute",
            StepType.CONDITIONAL: "conditional",
            StepType.CHAIN: "chain",
            StepType.PARALLEL: "parallel",
            StepType.VALIDATOR: "validator",
            StepType.WAIT_FOR_INPUT: "wait_for_input",
            StepType.API_CALL: "api_call",
        }
        
        # Get expected config field name for this step's type
        expected_field = step_config_fields.get(self.type)
        
        if expected_field is None:
            raise ValueError(f"Unknown step type: {self.type}")
            
        # Check if the expected configuration is present
        if getattr(self, expected_field) is None:
            raise ValueError(
                f"Step {self.id} is of type {self.type} but has no {expected_field} configuration"
            )
            
        return self