import logging
import os
from typing import List, Optional

from recipe_executor.context import Context
from recipe_executor.models import FileGenerationResult, FileSpec
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Attributes:
        artifact (str): Name of the context key holding a FileGenerationResult or List[FileSpec].
        root (str): Optional base path to prepend to all output file paths. Defaults to ".".
    """

    artifact: str
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    """
    WriteFilesStep writes generated files to disk based on content from the execution context.
    It handles template rendering, directory creation, and logging of file operations.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Convert dict config to WriteFilesConfig via Pydantic
        super().__init__(WriteFilesConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the write files step.

        Retrieves an artifact from the context, validates its type, and writes the corresponding files to disk.
        It supports both FileGenerationResult and a list of FileSpec objects.

        Args:
            context (Context): The execution context containing artifacts and configuration.

        Raises:
            ValueError: If the artifact is missing or if the root path rendering fails.
            TypeError: If the artifact is not a FileGenerationResult or a list of FileSpec objects.
            IOError: If an error occurs during file writing.
        """
        # Retrieve the artifact from the context
        data = context.get(self.config.artifact)
        if data is None:
            raise ValueError(f"No artifact found at key: {self.config.artifact}")

        # Determine the list of files to write
        if isinstance(data, FileGenerationResult):
            files: List[FileSpec] = data.files
        elif isinstance(data, list) and all(isinstance(f, FileSpec) for f in data):
            files = data
        else:
            raise TypeError("Expected FileGenerationResult or list of FileSpec objects")

        # Render the root output path using template rendering
        try:
            output_root = render_template(self.config.root, context)
        except Exception as e:
            raise ValueError(f"Error rendering root path '{self.config.root}': {str(e)}")

        # Process each file: resolve file path, create directories, and write the file
        for file in files:
            try:
                # Render the file path; file.path may contain template variables
                rel_path = render_template(file.path, context)
                full_path = os.path.join(output_root, rel_path)

                # Ensure that the parent directory exists
                parent_dir = os.path.dirname(full_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)

                # Write the file content using UTF-8 encoding
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(file.content)

                self.logger.info(f"Wrote file: {full_path}")
            except Exception as e:
                self.logger.error(f"Error writing file '{file.path}': {str(e)}")
                raise IOError(f"Error writing file '{file.path}': {str(e)}")
