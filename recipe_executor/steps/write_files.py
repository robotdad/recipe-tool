import os
import json
import logging
from typing import Any, Dict, List, Optional, Union

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol
from recipe_executor.models import FileSpec
from recipe_executor.utils.templates import render_template


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Attributes:
        files_key: Optional key in context containing FileSpec or list of FileSpec.
        files: Optional direct list of dict entries with path/content or keys.
        root: Base path for all output files.
    """
    files_key: Optional[str] = None
    files: Optional[List[Dict[str, Any]]] = None
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    """
    Step that writes one or more files to disk based on FileSpec or dict entries.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, WriteFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Determine source of file specifications
        if self.config.files is not None:
            files_source: Union[List[Any], FileSpec] = self.config.files  # type: ignore
        elif self.config.files_key:
            key = self.config.files_key
            if key not in context:
                raise KeyError(f"Context is missing files_key '{key}'")
            files_source = context[key]
        else:
            raise ValueError("Configuration must specify either 'files' or 'files_key'")

        # Normalize to a list
        if isinstance(files_source, FileSpec):  # single FileSpec
            entries: List[Any] = [files_source]
        elif isinstance(files_source, list):
            entries = files_source
        else:
            raise ValueError(f"Unsupported files source type: {type(files_source)}")

        # Render root directory
        try:
            rendered_root = render_template(self.config.root, context)
        except Exception as e:
            raise ValueError(f"Failed to render root path template '{self.config.root}': {e}")

        for entry in entries:
            # Determine path template and raw content
            if isinstance(entry, FileSpec):  # Pydantic model
                path_template = entry.path
                raw_content = entry.content
            elif isinstance(entry, dict):  # direct dict entry
                if "path" in entry:
                    path_template = entry["path"]
                elif "path_key" in entry:
                    key = entry["path_key"]
                    if key not in context:
                        raise KeyError(f"Context is missing path_key '{key}'")
                    path_template = context[key]
                else:
                    raise ValueError("File entry must contain 'path' or 'path_key'")

                if "content" in entry:
                    raw_content = entry["content"]
                elif "content_key" in entry:
                    key = entry["content_key"]
                    if key not in context:
                        raise KeyError(f"Context is missing content_key '{key}'")
                    raw_content = context[key]
                else:
                    raise ValueError("File entry must contain 'content' or 'content_key'")
            else:
                raise ValueError(f"Unsupported file entry type: {type(entry)}")

            # Render the file path
            try:
                rendered_path = render_template(path_template, context)
            except Exception as e:
                raise ValueError(f"Failed to render file path '{path_template}': {e}")

            # Compute full output path
            full_path = os.path.normpath(os.path.join(rendered_root, rendered_path))

            # Prepare content string
            if isinstance(raw_content, str):
                try:
                    content_str = render_template(raw_content, context)
                except Exception:
                    # No template variables or failed render; fall back to raw
                    content_str = raw_content
            else:
                # Preserve structure by dumping to JSON
                try:
                    content_str = json.dumps(raw_content, ensure_ascii=False, indent=2)
                except Exception as e:
                    raise ValueError(f"Failed to serialize content for '{full_path}': {e}")

            # Log debug info before writing
            self.logger.debug(
                f"Writing file '{full_path}' with content:\n{content_str}"
            )

            # Ensure directory exists
            dirpath = os.path.dirname(full_path)
            if dirpath:
                try:
                    os.makedirs(dirpath, exist_ok=True)
                except Exception as e:
                    raise RuntimeError(f"Failed to create directory '{dirpath}': {e}")

            # Write file to disk
            try:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content_str)
            except Exception as e:
                self.logger.error(f"Failed to write file '{full_path}': {e}")
                raise RuntimeError(f"Failed to write file '{full_path}': {e}")

            # Log success
            size = len(content_str.encode("utf-8"))
            self.logger.info(f"Wrote file '{full_path}' ({size} bytes)")


__all__ = ["WriteFilesConfig", "WriteFilesStep"]
