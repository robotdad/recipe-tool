import os
from .base import Step, register_step
from models import WriteFileConfig, CodeGenResult
from utils import render_template


@register_step('WriteFile')
class WriteFileStep(Step):
    def __init__(self, config, logger):
        self.config = WriteFileConfig(**config)
        self.logger = logger

    def execute(self, context):
        # Retrieve the code generation result from context
        result = context.get(self.config.input_key)
        if result is None:
            raise ValueError(f'No generated code found in context with key: {self.config.input_key}')

        # Allow overriding output root, else use context's output_root
        output_root = self.config.output_root or context.output_root
        self.logger.debug(f'Writing files to output root: {output_root}')

        # Write each file
        files_written = 0
        for file_spec in result.files:
            # Render file path and content if needed
            rendered_path = render_template(file_spec.path, context)
            rendered_content = render_template(file_spec.content, context)

            target_path = os.path.join(output_root, rendered_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            try:
                with open(target_path, 'w') as f:
                    f.write(rendered_content)
                self.logger.info(f'Wrote file: {target_path}')
                files_written += 1
            except Exception as e:
                self.logger.error(f'Error writing file "{target_path}": {e}')
                raise e
        self.logger.info(f'Total {files_written} file(s) written to "{output_root}".')
