import os

from recipe_executor.context import Context
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class ReadFileConfig(StepConfig):
    """
    Config for ReadFileStep.

    Fields:
        path: Path to the file to read (may be templated).
        artifact: Name to store the file contents in context.
    """

    path: str
    artifact: str


class ReadFileStep(BaseStep[ReadFileConfig]):
    """
    Step that reads a file and stores its contents in the context under the specified key.
    """

    def __init__(self, config: dict, logger=None):
        super().__init__(ReadFileConfig(**config), logger)

    def execute(self, context: Context) -> None:
        path = render_template(self.config.path, context)

        if not os.path.exists(path):
            raise FileNotFoundError(f"ReadFileStep: file not found at path: {path}")

        self.logger.info(f"Reading file from: {path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        context[self.config.artifact] = content
        self.logger.debug(f"Stored file contents in context under key: '{self.config.artifact}'")
