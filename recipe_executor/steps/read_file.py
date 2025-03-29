import logging
import os

from context import Context
from models import ReadFileConfig
from utils import render_template

from .base import Step, register_step


@register_step("readfile", ReadFileConfig)
class ReadFileStep(Step):
    def __init__(self, config: ReadFileConfig, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger

    def execute(self, context: Context) -> None:
        file_path = render_template(self.config.file_path, context)
        self.logger.debug(f"ReadFileStep: Reading file '{file_path}'.")
        input_root = context.get("input_root", ".")
        full_path = os.path.join(input_root, file_path) if not os.path.isabs(file_path) else file_path
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            context[self.config.store_key] = content
            self.logger.info(f"ReadFileStep: Successfully read file '{full_path}'.")
        except Exception as e:
            self.logger.error(f"ReadFileStep: Failed to read file '{full_path}': {e}")
            raise
