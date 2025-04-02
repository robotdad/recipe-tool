import logging
from typing import Any

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.context import Context
from recipe_executor.llm import call_llm
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
    """
    GenerateWithLLMStep is responsible for generating content using a large language model (LLM).
    It renders the prompt, model identifier, and artifact key from the provided context, calls the LLM,
    and stores the returned FileGenerationResult in the context under the rendered artifact key.
    
    The step follows a minimalistic design:
      - It uses template rendering for dynamic prompt and model resolution.
      - It allows the artifact key to be templated for dynamic context storage.
      - It logs details before and after calling the LLM.
    """

    def __init__(self, config: dict, logger: Any = None) -> None:
        """
        Initialize the GenerateWithLLMStep with its configuration and an optional logger.

        Args:
            config (dict): A dictionary containing the configuration for the step.
            logger (Optional[Any]): Logger instance to use for logging. Defaults to a logger with name "RecipeExecutor".
        """
        super().__init__(GenerateLLMConfig(**config), logger or logging.getLogger("RecipeExecutor"))

    def execute(self, context: Context) -> None:
        """
        Execute the LLM generation step using the provided context.
        
        This method performs the following:
          1. Dynamically render artifact key, prompt, and model values from the context.
          2. Log debug and info messages with details of the rendered parameters.
          3. Call the LLM using the rendered prompt and model.
          4. Store the resulting FileGenerationResult in the context under the rendered artifact key.
          5. Handle and log any errors encountered during generation.
        
        Args:
            context (Context): The shared context for execution containing input data and used for storing results.
        
        Raises:
            Exception: Propagates any exception encountered during processing, after logging the error.
        """
        try:
            # Process the artifact key using templating if needed
            artifact_key = self.config.artifact
            if "{{" in artifact_key and "}}" in artifact_key:
                artifact_key = render_template(artifact_key, context)

            # Render the prompt and model values using the current context
            rendered_prompt = render_template(self.config.prompt, context)
            rendered_model = render_template(self.config.model, context)

            # Log the LLM call details
            self.logger.info(f"Calling LLM with prompt for artifact: {artifact_key}")
            self.logger.debug(f"Rendered prompt: {rendered_prompt}")
            self.logger.debug(f"Rendered model: {rendered_model}")

            # Call the LLM to generate content
            response = call_llm(rendered_prompt, rendered_model, logger=self.logger)

            # Store the LLM response in the context
            context[artifact_key] = response
            self.logger.debug(f"LLM response stored in context under '{artifact_key}'")

        except Exception as e:
            # Log detailed error information for debugging
            self.logger.error(f"Failed to generate content using LLM. Error: {e}")
            raise
