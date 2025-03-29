import os

from recipe_executor.context import Context
from recipe_executor.models import FileGenerationResult, FileSpec
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFileStep.

    Fields:
        artifact: Name of the context key holding a CodeGenResult or List[FileSpec].
        root: Optional base path to prepend to all output file paths.
    """

    artifact: str
    root: str = "."


class WriteFileStep(BaseStep[WriteFilesConfig]):
    """
    Step that writes one or more files from context to disk.
    Accepts either a CodeGenResult or list of FileSpec dicts.
    """

    def __init__(self, config: dict, logger=None):
        super().__init__(WriteFilesConfig(**config), logger)

    def execute(self, context: Context) -> None:
        data = context.get(self.config.artifact)

        if data is None:
            raise ValueError(f"WriteFileStep: no artifact found at key: {self.config.artifact}")

        if isinstance(data, FileGenerationResult):
            files = data.files
        elif isinstance(data, list) and all(isinstance(f, FileSpec) for f in data):
            files = data
        else:
            raise TypeError("WriteFileStep: expected FileGenerationResult or list of FileSpec objects")

        output_root = render_template(self.config.root, context)

        for file in files:
            rel_path = render_template(file.path, context)
            full_path = os.path.join(output_root, rel_path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(file.content)

            self.logger.info(f"Wrote file: {full_path}")
