import os
from .base import Step, register_step
from models import ReadFileConfig
from utils import render_template


@register_step('ReadFile')
class ReadFileStep(Step):
    def __init__(self, config, logger):
        # Validate config using Pydantic model
        self.config = ReadFileConfig(**config)
        self.logger = logger

    def execute(self, context):
        # Render template for file path if needed
        file_path = render_template(self.config.file_path, context)
        full_path = file_path
        # If file_path is not absolute, join with context's input_root
        if not os.path.isabs(file_path):
            full_path = os.path.join(context.input_root, file_path)
        self.logger.debug(f'Reading file from: {full_path}')
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            context[self.config.store_key] = content
            self.logger.info(f'Read file "{full_path}" successfully and stored in context key "{self.config.store_key}".')
        except Exception as e:
            self.logger.error(f'Failed to read file "{full_path}": {e}')
            raise e
