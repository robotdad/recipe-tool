import json
import logging
from typing import Any, Dict

from models import CodeGenResult, GenerateCodeConfig
from utils import render_template

from .base import Step, register_step


@register_step("generatecode", GenerateCodeConfig)
class GenerateCodeStep(Step):
    def __init__(self, config: GenerateCodeConfig, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger
        self.system_prompt = (
            "You are a code generation assistant. Given a primary specification and supporting context, "
            "generate a JSON object with exactly two keys: 'files' and 'commentary'. The 'files' key must be a list "
            "of file objects, each with 'path' (a relative file path) and 'content' (the file content). "
            "The 'commentary' key is optional. Do not output any text outside the JSON structure."
        )
        from pydantic_ai import Agent

        self.agent = Agent(
            self.config.model if self.config.model else "openai:o3-mini",
            system_prompt=self.system_prompt,
            result_type=CodeGenResult,
        )

    def execute(self, context: Dict[str, Any]) -> None:
        input_spec = context.get(self.config.input_key)
        if input_spec is None:
            msg = f"GenerateCodeStep: Specification not found in context under key '{self.config.input_key}'."
            self.logger.error(msg)
            raise ValueError(msg)
        rendered_spec = render_template(input_spec, context)
        self.logger.info("GenerateCodeStep: Calling LLM with specification.")
        try:
            result = self.agent.run_sync(rendered_spec)
            structured_output = result.data  # Already a CodeGenResult object.
            context[self.config.output_key] = structured_output
            self.logger.info("GenerateCodeStep: Code generation completed successfully.")
            self.logger.debug(f"GenerateCodeStep: Generated output: {json.dumps(structured_output.dict())}")
        except Exception as e:
            self.logger.error(f"GenerateCodeStep: LLM call failed: {e}", exc_info=True)
            raise
