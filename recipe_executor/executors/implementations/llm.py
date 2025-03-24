"""LLM generation executor implementation."""

import asyncio
import hashlib
import json
import logging
import os
from typing import Any, Dict, List, Optional, Type

import yaml
from pydantic import BaseModel, Field, create_model
from pydantic_ai import Agent

from recipe_executor.constants import OutputFormat
from recipe_executor.context.execution_context import ExecutionContext
from recipe_executor.models.base import FilesGenerationResult
from recipe_executor.models.events import LLMGenerationEvent
from recipe_executor.models.step import RecipeStep
from recipe_executor.models.validation import ValidationIssue, ValidationResult

logger = logging.getLogger("recipe-executor")


class LLMGenerateExecutor:
    """Executor for LLM generation steps."""

    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the executor."""
        self.agents_cache = {}
        self.cache_dir = cache_dir
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)

    def _get_agent(
        self,
        model_provider: str,
        model_name: str,
        result_type: Type,
        system_prompt: Optional[str] = None,
        temp: Optional[float] = None,
    ) -> Agent:
        """Get an agent from the cache or create a new one."""
        cache_key = f"{model_provider}:{model_name}:{result_type.__name__}:{system_prompt}:{temp}"
        if cache_key not in self.agents_cache:
            # Format model ID properly for pydantic-ai
            if model_provider == "anthropic":
                model_id = (
                    f"anthropic:{model_name}"
                    if not model_name.startswith("anthropic:")
                    else model_name
                )
            elif model_provider == "openai":
                model_id = model_name  # OpenAI doesn't need a prefix
            else:
                model_id = f"{model_provider}:{model_name}"

            # Set up model settings
            model_settings = {"temperature": temp if temp is not None else 0.1}

            # Create the agent with proper handling of system_prompt
            agent_kwargs = {
                "model": model_id,
                "result_type": result_type,
                "model_settings": model_settings,
            }

            # Only add system_prompt if it's not None
            if system_prompt is not None:
                agent_kwargs["system_prompt"] = system_prompt

            agent = Agent(**agent_kwargs)
            self.agents_cache[cache_key] = agent
        return self.agents_cache[cache_key]

    async def _create_dynamic_model(
        self, schema: Dict[str, Any], context: ExecutionContext
    ) -> Type[BaseModel]:
        """
        Create a Pydantic model dynamically from a schema.

        Args:
            schema: Schema definition for the model
            context: Execution context

        Returns:
            Dynamically created Pydantic model
        """
        # Extract the fields from the schema
        fields = {}
        for field_name, field_def in schema.get("properties", {}).items():
            field_type = field_def.get("type")
            description = field_def.get("description", "")

            if field_type == "string":
                fields[field_name] = (str, Field(description=description))
            elif field_type == "integer":
                fields[field_name] = (int, Field(description=description))
            elif field_type == "number":
                fields[field_name] = (float, Field(description=description))
            elif field_type == "boolean":
                fields[field_name] = (bool, Field(description=description))
            elif field_type == "array":
                items = field_def.get("items", {})
                item_type = items.get("type", "string")
                if item_type == "string":
                    fields[field_name] = (List[str], Field(description=description))
                elif item_type == "integer":
                    fields[field_name] = (List[int], Field(description=description))
                elif item_type == "number":
                    fields[field_name] = (List[float], Field(description=description))
                elif item_type == "boolean":
                    fields[field_name] = (List[bool], Field(description=description))
                else:
                    fields[field_name] = (List[Any], Field(description=description))
            elif field_type == "object":
                # For now, treat nested objects as dictionaries
                fields[field_name] = (Dict[str, Any], Field(description=description))
            else:
                # Default to Any for unknown types
                fields[field_name] = (Any, Field(description=description))

        # Create the model with the extracted fields
        model_name = schema.get("title", "DynamicModel")
        model = create_model(model_name, **fields)
        return model

    async def execute(self, step: RecipeStep, context: ExecutionContext) -> Any:
        """
        Execute an LLM generation step.

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            Generated content from the LLM
        """
        if not step.llm_generate:
            raise ValueError(f"Missing llm_generate configuration for step {step.id}")

        config = step.llm_generate
        prompt = context.interpolate_variables(config.prompt)

        # Emit LLM generation event
        event = LLMGenerationEvent(
            model=config.model or "default", prompt_length=len(prompt)
        )
        context.emit_event(event)

        # Determine which model to use
        model_provider = "anthropic"
        model_name = config.model

        if context.recipe and context.recipe.model:
            model_provider = context.recipe.model.provider
            if not model_name:
                model_name = context.recipe.model.model_name

        if not model_name:
            model_name = "claude-3-7-sonnet-20250219"

        # Get the temperature
        temp = config.temperature
        if temp is None and context.recipe and context.recipe.model:
            temp = context.recipe.model.temperature

        # Get the system prompt
        system_prompt = None
        if (
            context.recipe
            and context.recipe.model
            and context.recipe.model.system_prompt
        ):
            system_prompt = context.interpolate_variables(
                context.recipe.model.system_prompt
            )

        # Cache key for result type and prompt
        cache_key = None
        if self.cache_dir:
            h = hashlib.md5()
            h.update(prompt.encode("utf-8"))
            if system_prompt:
                h.update(system_prompt.encode("utf-8"))
            h.update(str(config.output_format).encode("utf-8"))
            if config.structured_schema:
                h.update(json.dumps(config.structured_schema).encode("utf-8"))
            cache_key = h.hexdigest()
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

            # Check if we have a cached result
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, "r") as f:
                        cached_data = json.load(f)
                    logger.info(f"Using cached result for step {step.id}")
                    return cached_data.get("result")
                except Exception as e:
                    logger.warning(f"Failed to load cached result: {e}")

        # Prepare message history if needed
        message_history = None
        if config.include_history:
            message_history = context.get_message_history(step.id)
        elif config.history_variable and config.history_variable in context.variables:
            history_var = context.get_variable(config.history_variable)
            # Check if history_var is a list and its items have the appropriate attributes
            if isinstance(history_var, list) and all(
                hasattr(msg, "role") and hasattr(msg, "content") for msg in history_var
            ):
                message_history = history_var

        # Handle structured output
        result_type: Type = str

        if config.output_format == OutputFormat.JSON:
            result_type = Dict[str, Any]
        elif config.output_format == OutputFormat.FILES:
            result_type = FilesGenerationResult
        elif config.output_format == OutputFormat.STRUCTURED:
            # Create a dynamic model from the schema
            schema = None

            if config.structured_schema:
                schema = config.structured_schema
            elif config.structured_schema_file:
                schema_file = context.interpolate_variables(
                    config.structured_schema_file
                )
                try:
                    with open(schema_file, "r") as f:
                        if schema_file.endswith(".json"):
                            schema = json.load(f)
                        elif schema_file.endswith((".yaml", ".yml")):
                            schema = yaml.safe_load(f)
                        else:
                            raise ValueError(
                                f"Unsupported schema file format: {schema_file}"
                            )
                except Exception as e:
                    logger.error(f"Error loading schema file {schema_file}: {e}")
                    raise

            if schema:
                result_type = await self._create_dynamic_model(schema, context)
            else:
                # Default to Dict if no schema provided
                result_type = Dict[str, Any]

        # Set up timeout handling
        timeout = config.timeout
        if timeout is None and step.timeout:
            timeout = step.timeout
        if timeout is None and context.recipe and context.recipe.timeout:
            timeout = context.recipe.timeout

        # Get the agent
        agent = self._get_agent(
            model_provider=model_provider,
            model_name=model_name,
            result_type=result_type,
            system_prompt=system_prompt,
            temp=temp,
        )

        # Run the agent with timeout if specified
        if timeout:
            try:
                result = await asyncio.wait_for(
                    agent.run(
                        prompt,
                        message_history=message_history,
                    ),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                logger.error(
                    f"LLM generation timed out after {timeout}s for step {step.id}"
                )
                raise TimeoutError(f"LLM generation timed out after {timeout}s")
        else:
            result = await agent.run(
                prompt,
                message_history=message_history,
            )

        # Store the message history
        context.set_message_history(step.id, result.new_messages())

        # Store the result in the cache if enabled
        if cache_key and self.cache_dir:
            try:
                with open(os.path.join(self.cache_dir, f"{cache_key}.json"), "w") as f:
                    json.dump(
                        {
                            "prompt": prompt,
                            "system_prompt": system_prompt,
                            "result": result.data,
                        },
                        f,
                    )
            except Exception as e:
                logger.warning(f"Failed to cache result: {e}")

        return result.data

    async def validate_result(
        self, step: RecipeStep, result: Any, context: ExecutionContext
    ) -> ValidationResult:
        """
        Validate the result of an LLM generation step.

        Args:
            step: Step to validate
            result: Result to validate
            context: Execution context

        Returns:
            Validation result
        """
        if not step.llm_generate:
            return ValidationResult(valid=True, issues=[])

        config = step.llm_generate

        # For structured output, the validation is done by Pydantic
        if (
            config.output_format == OutputFormat.STRUCTURED
            and config.validation_criteria
        ):
            issues = []
            valid = True

            for criterion_name, criterion_config in config.validation_criteria.items():
                criterion_type = criterion_config.get("type", "presence")
                field_path = criterion_config.get("field", "")

                # Get the field value
                field_value = result
                if field_path:
                    for part in field_path.split("."):
                        if isinstance(field_value, dict) and part in field_value:
                            field_value = field_value[part]
                        else:
                            field_value = None
                            break

                # Validate based on criterion type
                if criterion_type == "presence" and field_value is None:
                    issues.append(
                        ValidationIssue(
                            message=f"Field {field_path} is required but missing",
                            severity="error",
                            path=field_path,
                        )
                    )
                    valid = False
                elif criterion_type == "non_empty" and (
                    field_value is None
                    or field_value == ""
                    or field_value == []
                    or field_value == {}
                ):
                    issues.append(
                        ValidationIssue(
                            message=f"Field {field_path} must not be empty",
                            severity="error",
                            path=field_path,
                        )
                    )
                    valid = False
                elif (
                    criterion_type == "min_length"
                    and isinstance(field_value, (str, list))
                    and len(field_value) < criterion_config.get("value", 0)
                ):
                    issues.append(
                        ValidationIssue(
                            message=f"Field {field_path} must have length at least {criterion_config.get('value', 0)}",
                            severity="error",
                            path=field_path,
                        )
                    )
                    valid = False
                elif (
                    criterion_type == "max_length"
                    and isinstance(field_value, (str, list))
                    and len(field_value) > criterion_config.get("value", float("inf"))
                ):
                    issues.append(
                        ValidationIssue(
                            message=f"Field {field_path} must have length at most {criterion_config.get('value', float('inf'))}",
                            severity="error",
                            path=field_path,
                        )
                    )
                    valid = False
                elif criterion_type == "custom" and "condition" in criterion_config:
                    condition = criterion_config["condition"]
                    # Replace field references with actual values
                    condition = condition.replace("field_value", repr(field_value))

                    try:
                        if not eval(condition):
                            issues.append(
                                ValidationIssue(
                                    message=criterion_config.get(
                                        "message",
                                        f"Field {field_path} failed custom validation",
                                    ),
                                    severity="error",
                                    path=field_path,
                                )
                            )
                            valid = False
                    except Exception as e:
                        issues.append(
                            ValidationIssue(
                                message=f"Error evaluating custom condition for {field_path}: {e}",
                                severity="error",
                                path=field_path,
                            )
                        )
                        valid = False

            return ValidationResult(valid=valid, issues=issues)

        # For file generation, check that all files are valid
        if config.output_format == OutputFormat.FILES and isinstance(
            result, FilesGenerationResult
        ):
            issues = []
            valid = True

            if not result.completed:
                issues.append(
                    ValidationIssue(
                        message="File generation was marked as incomplete",
                        severity="error",
                    )
                )
                valid = False

            if not result.files:
                issues.append(
                    ValidationIssue(message="No files were generated", severity="error")
                )
                valid = False

            for i, file in enumerate(result.files):
                if not file.path:
                    issues.append(
                        ValidationIssue(
                            message=f"File {i + 1} has no path",
                            severity="error",
                            path=f"files[{i}].path",
                        )
                    )
                    valid = False

                if not file.content:
                    issues.append(
                        ValidationIssue(
                            message=f"File {i + 1} ({file.path}) has no content",
                            severity="warning",
                            path=f"files[{i}].content",
                        )
                    )

            return ValidationResult(valid=valid, issues=issues)

        # Default validation for text output
        return ValidationResult(valid=True, issues=[])
