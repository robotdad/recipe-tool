import logging
from pathlib import Path
from typing import Any, Dict, List, Union

from pydantic import validator

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
            - "concat" (default): Concatenate all files with newlines between each file’s content
            - "dict": Store a dictionary with filenames as keys and content as values
    """

    path: Union[str, List[str]]
    content_key: str
    optional: bool = False
    merge_mode: str = "concat"

    @validator("merge_mode")
    def _validate_merge_mode(cls, v: str) -> str:
        if v not in ("concat", "dict"):
            raise ValueError("merge_mode must be either 'concat' or 'dict'")
        return v


class ReadFilesStep(BaseStep[ReadFilesConfig]):
    """
    Step that reads one or more files from the filesystem, optionally merges their content,
    and stores the result in the context under a specified key.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ReadFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Resolve and normalize paths
        raw_path = self.config.path
        paths: List[str] = []

        if isinstance(raw_path, str):
            # Render template on the whole string
            rendered = render_template(raw_path, context)
            # Split comma-separated
            if "," in rendered:
                parts = [p.strip() for p in rendered.split(",") if p.strip()]
                paths = parts
            else:
                paths = [rendered]
        elif isinstance(raw_path, list):
            # Render each entry
            for entry in raw_path:
                if not isinstance(entry, str):
                    raise ValueError(f"Invalid path entry type: {type(entry)}")
                rendered = render_template(entry, context)
                paths.append(rendered)
        else:
            raise ValueError(f"Invalid path parameter type: {type(raw_path)}")

        contents: List[str] = []
        content_dict: Dict[str, str] = {}

        # Process each file
        for path_str in paths:
            path_obj = Path(path_str)
            self.logger.debug(f"Attempting to read file: {path_str}")
            if not path_obj.exists():
                msg = f"File not found: {path_str}"
                if self.config.optional:
                    self.logger.warning(f"Optional file missing, skipping: {path_str}")
                    # For single optional, store empty later; for multiple, skip
                    continue
                else:
                    raise FileNotFoundError(msg)
            # Read file
            try:
                content = path_obj.read_text(encoding="utf-8")
                self.logger.info(f"Successfully read file: {path_str}")
            except Exception as e:
                raise RuntimeError(f"Error reading file '{path_str}': {e}")

            if self.config.merge_mode == "concat":
                contents.append(content)
            else:  # dict mode
                content_dict[path_str] = content

        # Determine final content
        if len(paths) == 1:
            # Single file semantics
            if contents:
                result = contents[0]
            else:
                # File missing but optional
                result = ""
        else:
            if self.config.merge_mode == "concat":
                result = "\n".join(contents)
            else:
                result = content_dict

        # Store in context
        context[self.config.content_key] = result
        self.logger.info(f"Stored file content under key '{self.config.content_key}'")
