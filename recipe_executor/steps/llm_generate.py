"""
LLMGenerateStep component: generate content via LLMs with templating, MCP tools, and structured output.
"""
from typing import Any, Dict, List, Optional, Type, Union
import logging

from pydantic import BaseModel

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol
from recipe_executor.utils.templates import render_template
from recipe_executor.llm_utils.llm import LLM
from recipe_executor.llm_utils.mcp import get_mcp_server
from recipe_executor.models import FileSpec
from recipe_executor.utils.models import json_schema_to_pydantic_model


class LLMGenerateConfig(StepConfig):  # type: ignore
    """
    Config for LLMGenerateStep.

    Fields:
        prompt: templated prompt string for the LLM
        model: templated model identifier (provider/model_name)
        mcp_servers: optional list of MCP server configs
        output_format: 'text', 'files', or a JSON schema dict
        output_key: templated key to store output in context
    """
    prompt: str
    model: str = "openai/gpt-4o"
    mcp_servers: Optional[List[Dict[str, Any]]] = None
    output_format: Union[str, Dict[str, Any]]
    output_key: str = "llm_output"


class FileSpecCollection(BaseModel):
    files: List[FileSpec]


class LLMGenerateStep(BaseStep[LLMGenerateConfig]):
    """
    Step to generate content from an LLM, supporting text, files, or JSON-schema outputs.
    """
    def __init__(
        self,
        logger: logging.Logger,
        config: Dict[str, Any]
    ) -> None:
        super().__init__(logger, LLMGenerateConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Render templates for prompt, model, and output key
        rendered_prompt = render_template(self.config.prompt, context)
        rendered_model = render_template(self.config.model, context)
        rendered_output_key = render_template(self.config.output_key, context)

        # Prepare MCP servers if any
        mcp_servers: List[Any] = []
        if self.config.mcp_servers:
            for raw_cfg in self.config.mcp_servers:
                rendered_cfg: Dict[str, Any] = {}
                for k, v in raw_cfg.items():  # render string values
                    if isinstance(v, str):
                        rendered_cfg[k] = render_template(v, context)
                    else:
                        rendered_cfg[k] = v
                mcp_server = get_mcp_server(logger=self.logger, config=rendered_cfg)
                mcp_servers.append(mcp_server)

        # Instantiate LLM with rendered model and MCP servers
        llm = LLM(logger=self.logger, model=rendered_model, mcp_servers=mcp_servers or None)

        # Determine output type for LLM call
        fmt = self.config.output_format
        if isinstance(fmt, str):
            if fmt == "text":
                output_type: Type[Union[str, BaseModel]] = str  # plain text
            elif fmt == "files":
                output_type = FileSpecCollection  # structured file specs
            else:
                raise ValueError(f"Unsupported output_format: {fmt}")
        else:
            # JSON schema provided: build dynamic Pydantic model
            output_type = json_schema_to_pydantic_model(fmt, model_name="LLMGenerateOutput")

        # Log and call LLM
        self.logger.debug(
            f"Invoking LLM.generate(model={rendered_model}, prompt...)"
        )
        try:
            # generate returns str or BaseModel instance
            result = await llm.generate(
                prompt=rendered_prompt,
                output_type=output_type
            )
        except Exception as e:
            self.logger.error(f"LLM.generate failed: {e}")
            raise

        # Process and store the result in context
        if isinstance(fmt, str):
            if fmt == "text":
                context[rendered_output_key] = result  # type: ignore
            else:  # files
                # result is FileSpecCollection
                files = []
                # model_dump for each FileSpec to get plain dict
                for spec in result.files:  # type: ignore
                    if isinstance(spec, BaseModel):  # Pydantic FileSpec
                        files.append(spec.model_dump())
                    else:
                        files.append(spec)
                context[rendered_output_key] = files
        else:
            # JSON/schema case: result is BaseModel
            if isinstance(result, BaseModel):
                context[rendered_output_key] = result.model_dump()
            else:
                context[rendered_output_key] = result  # fallback
