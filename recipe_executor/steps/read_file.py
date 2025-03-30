import logging
import os
from typing import Optional

from recipe_executor.context import Context
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class ReadFileConfig(StepConfig):
    """
    Configuration for ReadFileStep.

    Attributes:
        path (str): Path to the file to read (may be templated).
        artifact (str): Name to store the file contents in context.
        optional (bool): Whether to continue if the file is not found. Defaults to False.
    """

    path: str
    artifact: str
    optional: bool = False


class ReadFileStep(BaseStep[ReadFileConfig]):
    """
    Step that reads a file from the filesystem using a template-resolved path and stores its contents in the execution context.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Convert dict to ReadFileConfig using Pydantic validation
        super().__init__(ReadFileConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the file reading step.

        This method resolves the file path from the provided template, reads its content if file exists,
        and stores the content into the given execution context under the specified artifact key.
        If the file is marked as optional and not found, it logs a warning and stores an empty string.

        Args:
            context (Context): The shared execution context.

        Raises:
            FileNotFoundError: If the file is not found and the step is not marked as optional.
            Exception: Re-raises any exceptions encountered while reading the file.
        """
        # Render the file path using the current context
        rendered_path: str = render_template(self.config.path, context)

        # Check file existence
        if not os.path.exists(rendered_path):
            if self.config.optional:
                self.logger.warning(f"Optional file not found at path: {rendered_path}, continuing with empty content")
                context[self.config.artifact] = ""
                return
            else:
                raise FileNotFoundError(f"ReadFileStep: file not found at path: {rendered_path}")

        self.logger.info(f"Reading file from: {rendered_path}")
        try:
            with open(rendered_path, "r", encoding="utf-8") as file:
                content = file.read()
        except Exception as exc:
            self.logger.error(f"Error reading file at path: {rendered_path}. Exception: {exc}")
            raise

        # Store the file content in the context under the specified artifact key
        context[self.config.artifact] = content
        self.logger.debug(f"Stored file contents in context under key: '{self.config.artifact}'")
