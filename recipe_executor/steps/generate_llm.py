from recipe_executor.context import Context
from recipe_executor.llm import call_llm
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class GenerateLLMConfig(StepConfig):
    """
    Config for GenerateWithLLMStep.

    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        artifact: The name under which to store the LLM response in context.
    """

    prompt: str
    model: str
    artifact: str


class GenerateWithLLMStep(BaseStep[GenerateLLMConfig]):
    """
    Step that calls an LLM with a prompt and stores the result as a context artifact.
    """

    def __init__(self, config: dict, logger=None) -> None:
        super().__init__(GenerateLLMConfig(**config), logger)

    def execute(self, context: Context) -> None:
        # Process the artifact key using templating if needed.
        artifact_key = self.config.artifact
        self.logger.debug("Original artifact key: %s", artifact_key)
        if "{{" in artifact_key and "}}" in artifact_key:
            artifact_key = render_template(artifact_key, context)
        self.logger.debug("Artifact key after rendering: %s", artifact_key)

        # Render the prompt with the current context to substitute template placeholders.
        rendered_prompt = render_template(self.config.prompt, context)
        rendered_model = render_template(self.config.model, context)
        self.logger.info(f"Calling LLM with prompt for artifact: {artifact_key}")
        response = call_llm(rendered_prompt, rendered_model)

        # Store the LLM response in context under the rendered artifact key.
        context[artifact_key] = response
        self.logger.debug("LLM response stored in context under '%s'", artifact_key)
