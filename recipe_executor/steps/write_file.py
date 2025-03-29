import logging
import os
from typing import Any, Dict

from models import CodeGenResult, WriteFileConfig
from utils import render_template

from .base import Step, register_step


@register_step("writefile", WriteFileConfig)
class WriteFileStep(Step):
    def __init__(self, config: WriteFileConfig, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger

    def execute(self, context: Dict[str, Any]) -> None:
        self.logger.info("WriteFileStep: Starting to write generated files.")
        codegen_result: CodeGenResult = context.get(self.config.input_key)
        if codegen_result is None:
            msg = f"WriteFileStep: Code generation result not found in context under key '{self.config.input_key}'."
            self.logger.error(msg)
            raise ValueError(msg)
        output_root = self.config.output_root or context.get("output_root", ".")
        count = 0
        for file_spec in codegen_result.files:
            file_path = render_template(file_spec.path, context)
            full_path = os.path.join(output_root, file_path) if not os.path.isabs(file_path) else file_path
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            try:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(file_spec.content)
                self.logger.debug(f"WriteFileStep: Written file '{full_path}'.")
                count += 1
            except Exception as e:
                self.logger.error(f"WriteFileStep: Failed to write file '{full_path}': {e}")
                raise
        self.logger.info(f"WriteFileStep: Successfully written {count} files to '{output_root}'.")
