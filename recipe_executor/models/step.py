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
        if self.type == StepType.LLM_GENERATE and not self.llm_generate:
            raise ValueError(
                f"Step {self.id} is of type LLM_GENERATE but has no llm_generate configuration"
            )
        if self.type == StepType.FILE_READ and not self.file_read:
            raise ValueError(
                f"Step {self.id} is of type FILE_READ but has no file_read configuration"
            )
        if self.type == StepType.FILE_WRITE and not self.file_write:
            raise ValueError(
                f"Step {self.id} is of type FILE_WRITE but has no file_write configuration"
            )
        if self.type == StepType.TEMPLATE_SUBSTITUTE and not self.template_substitute:
            raise ValueError(
                f"Step {self.id} is of type TEMPLATE_SUBSTITUTE but has no template_substitute configuration"
            )
        if self.type == StepType.JSON_PROCESS and not self.json_process:
            raise ValueError(
                f"Step {self.id} is of type JSON_PROCESS but has no json_process configuration"
            )
        if self.type == StepType.PYTHON_EXECUTE and not self.python_execute:
            raise ValueError(
                f"Step {self.id} is of type PYTHON_EXECUTE but has no python_execute configuration"
            )
        if self.type == StepType.CONDITIONAL and not self.conditional:
            raise ValueError(
                f"Step {self.id} is of type CONDITIONAL but has no conditional configuration"
            )
        if self.type == StepType.CHAIN and not self.chain:
            raise ValueError(
                f"Step {self.id} is of type CHAIN but has no chain configuration"
            )
        if self.type == StepType.PARALLEL and not self.parallel:
            raise ValueError(
                f"Step {self.id} is of type PARALLEL but has no parallel configuration"
            )
        if self.type == StepType.VALIDATOR and not self.validator:
            raise ValueError(
                f"Step {self.id} is of type VALIDATOR but has no validator configuration"
            )
        if self.type == StepType.WAIT_FOR_INPUT and not self.wait_for_input:
            raise ValueError(
                f"Step {self.id} is of type WAIT_FOR_INPUT but has no wait_for_input configuration"
            )
        if self.type == StepType.API_CALL and not self.api_call:
            raise ValueError(
                f"Step {self.id} is of type API_CALL but has no api_call configuration"
            )
        return self
