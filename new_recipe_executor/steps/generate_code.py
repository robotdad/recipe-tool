from .base import Step, register_step
from models import GenerateCodeConfig, CodeGenResult, FileSpec
from utils import render_template
import json


@register_step('GenerateCode')
class GenerateCodeStep(Step):
    def __init__(self, config, logger):
        self.config = GenerateCodeConfig(**config)
        self.logger = logger

    def execute(self, context):
        # Retrieve prompt/specification from context
        spec_source = context.get(self.config.input_key)
        if spec_source is None:
            raise ValueError(f'No input found in context with key: {self.config.input_key}')
        # Render the spec template using context
        rendered_spec = render_template(self.config.spec, context)
        self.logger.debug(f'Rendered spec for GenerateCode: {rendered_spec}')

        # Simulate LLM call (in actual implementation, use pydantic-ai agent here)
        # For demonstration, we generate a dummy code file
        dummy_file = FileSpec(path='generated/hello.py', content='#!/usr/bin/env python\nprint("Hello, World!")')
        result = CodeGenResult(files=[dummy_file], commentary='Dummy generation successful.')

        # Store the result in context
        context[self.config.output_key] = result
        self.logger.info(f'Generated code stored in context key "{self.config.output_key}".')
