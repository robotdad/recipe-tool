import logging
from typing import Optional

from recipe_executor.context import Context
from recipe_executor.llm import call_llm
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class GenerateLLMConfig(StepConfig):
    """
    Config for GenerateWithLLMStep.

    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        model: The model identifier to use (provider:model_name format).
        artifact: The name under which to store the LLM response in context.
    """

    prompt: str
    model: str
    artifact: str


class GenerateWithLLMStep(BaseStep[GenerateLLMConfig]):
    """Component that generates content using a Large Language Model (LLM)."""

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Convert the configuration dictionary to the GenerateLLMConfig type
        super().__init__(GenerateLLMConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the generate step:
          - Render the artifact key if templated
          - Render the prompt and model using the context
          - Call the LLM with the rendered prompt and model
          - Store the generation result in the context under the resolved artifact key

        Args:
            context (Context): The execution context containing artifacts and variables.

        Raises:
            ValueError: If template rendering fails.
            RuntimeError: If LLM call fails.
        """
        # Process artifact key rendering
        artifact_key = self.config.artifact
        try:
            if "{{" in artifact_key and "}}" in artifact_key:
                artifact_key = render_template(artifact_key, context)
        except Exception as e:
            self.logger.error("Error rendering artifact key '%s': %s", self.config.artifact, e)
            raise ValueError(f"Error rendering artifact key: {e}")

        # Render prompt and model using the current context
        try:
            rendered_prompt = render_template(self.config.prompt, context)
            rendered_model = render_template(self.config.model, context)
        except Exception as e:
            self.logger.error("Error rendering prompt or model: %s", e)
            raise ValueError(f"Error rendering templates: {e}")

        # Log LLM call initiation
        self.logger.info("Calling LLM with prompt for artifact: %s", artifact_key)

        # Call the LLM and handle potential failures
        try:
            response = call_llm(rendered_prompt, rendered_model)
        except Exception as e:
            self.logger.error("LLM call failed for model '%s' with prompt '%s': %s", rendered_model, rendered_prompt, e)
            raise RuntimeError(f"LLM call failed: {e}")

        # Store the result in context under the resolved artifact key
        context[artifact_key] = response
        self.logger.debug("LLM response stored in context under '%s'", artifact_key)
