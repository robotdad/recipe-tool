import json
import logging
import os
from typing import Any, Dict, List, Union

import yaml

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template


class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path, comma-separated string, or list of paths to the file(s) to read (may be templated).
        content_key (str): Name to store the file content in context.
        optional (bool): Whether to continue if a file is not found.
        merge_mode (str): How to handle multiple files' content. Options:
            - "concat" (default): Concatenate all files with newlines between filenames + content
            - "dict": Store a dictionary with filenames as keys and content as values
    """

    path: Union[str, List[str]]
    content_key: str
    optional: bool = False
    merge_mode: str = "concat"


class ReadFilesStep(BaseStep[ReadFilesConfig]):
    """
    Step that reads one or more files from disk and stores their content in the execution context.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ReadFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        cfg = self.config
        raw_path = cfg.path
        paths: List[str] = []

        # Resolve and normalize paths
        if isinstance(raw_path, str):
            rendered = render_template(raw_path, context)
            # Split comma-separated
            if "," in rendered:
                parts = [p.strip() for p in rendered.split(",") if p.strip()]
                paths = parts
            else:
                paths = [rendered]
        elif isinstance(raw_path, list):
            for p in raw_path:
                if not isinstance(p, str):
                    raise ValueError(f"Invalid path entry: {p!r}")
                rendered = render_template(p, context)
                paths.append(rendered)
        else:
            raise ValueError(f"Invalid type for path: {type(raw_path)}")

        results: List[Any] = []
        result_dict: Dict[str, Any] = {}

        for path in paths:
            self.logger.debug(f"Reading file at path: {path}")
            if not os.path.exists(path):
                msg = f"File not found: {path}"
                if cfg.optional:
                    self.logger.warning(f"Optional file missing, skipping: {path}")
                    continue
                raise FileNotFoundError(msg)

            # Read file content
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            # Attempt deserialization if applicable
            ext = os.path.splitext(path)[1].lower()
            content: Any
            try:
                if ext == ".json":
                    content = json.loads(text)
                elif ext in (".yaml", ".yml"):
                    content = yaml.safe_load(text)
                else:
                    content = text
            except Exception as e:
                self.logger.warning(f"Failed to parse structured data from {path}: {e}")
                content = text

            self.logger.info(f"Successfully read file: {path}")
            results.append(content)
            result_dict[path] = content

        # Merge results
        final_content: Any
        if not results:
            # No files read
            if len(paths) <= 1:
                final_content = ""  # single missing
            elif cfg.merge_mode == "dict":
                final_content = {}
            else:
                final_content = ""
        elif len(results) == 1:
            # Single file
            final_content = results[0]
        else:
            # Multiple files
            if cfg.merge_mode == "dict":
                final_content = result_dict
            else:
                # concat mode
                parts: List[str] = []
                for p in paths:
                    if p in result_dict:
                        raw = result_dict[p]
                        parts.append(f"{p}\n{raw}")
                final_content = "\n".join(parts)

        # Store in context
        context[cfg.content_key] = final_content
        self.logger.info(f"Stored file content under key '{cfg.content_key}'")
