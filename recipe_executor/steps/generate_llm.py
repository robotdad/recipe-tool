from recipe_executor.context import Context
from recipe_executor.llm import call_llm
from recipe_executor.steps.base import BaseStep, StepConfig


class GenerateLLMConfig(StepConfig):
    """
    Config for GenerateWithLLMStep.

    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        artifact: The name under which to store the LLM response in context.
    """

    prompt: str
    artifact: str


class GenerateWithLLMStep(BaseStep[GenerateLLMConfig]):
    """
    Step that calls an LLM with a prompt and stores the result as a context artifact.
    """

    def __init__(self, config: dict, logger=None) -> None:
        super().__init__(GenerateLLMConfig(**config), logger)

    def execute(self, context: Context) -> None:
        self.logger.info(f"Calling LLM with prompt for artifact: {self.config.artifact}")
        response = call_llm(self.config.prompt)
        context[self.config.artifact] = response
        self.logger.debug(f"LLM response stored in context under '{self.config.artifact}'")
