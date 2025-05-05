import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

from recipe_executor.models import FileSpec
from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template


class WriteFilesConfig(StepConfig):
    """
    Configuration for WriteFilesStep.

    Attributes:
        files_key: Optional context key containing FileSpec or list/dict specs.
        files: Optional direct list of dicts with 'path'/'content' or their key references.
        root: Base directory for output files.
    """
    files_key: Optional[str] = None
    files: Optional[List[Dict[str, Any]]] = None
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    """
    Step that writes one or more files to disk based on FileSpec or dict inputs.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, WriteFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Resolve and render the root output directory
        raw_root: str = self.config.root or "."
        root: str = render_template(raw_root, context)

        files_to_write: List[Dict[str, Any]] = []

        # 1. Direct 'files' entries take precedence
        if self.config.files is not None:
            for entry in self.config.files:
                # Path extraction
                if "path" in entry:
                    raw_path = entry["path"]
                elif "path_key" in entry:
                    key = entry["path_key"]
                    if key not in context:
                        raise KeyError(f"Path key '{key}' not found in context.")
                    raw_path = context[key]
                else:
                    raise ValueError("Each file entry must have 'path' or 'path_key'.")
                path_str = str(raw_path)
                path = render_template(path_str, context)

                # Content extraction
                if "content" in entry:
                    raw_content = entry["content"]
                elif "content_key" in entry:
                    key = entry["content_key"]
                    if key not in context:
                        raise KeyError(f"Content key '{key}' not found in context.")
                    raw_content = context[key]
                else:
                    raise ValueError("Each file entry must have 'content' or 'content_key'.")

                files_to_write.append({"path": path, "content": raw_content})

        # 2. Use files from context via 'files_key'
        elif self.config.files_key:
            key = self.config.files_key
            if key not in context:
                raise KeyError(f"Files key '{key}' not found in context.")
            raw = context[key]

            if isinstance(raw, FileSpec):
                items: List[Union[FileSpec, Dict[str, Any]]] = [raw]
            elif isinstance(raw, dict):  # dict spec
                if "path" in raw and "content" in raw:
                    items = [raw]
                else:
                    raise ValueError(f"Malformed file dict under key '{key}': {raw}")
            elif isinstance(raw, list):  # list of specs
                items = raw  # type: ignore
            else:
                raise ValueError(f"Unsupported type for files_key '{key}': {type(raw)}")

            for item in items:
                if isinstance(item, FileSpec):
                    raw_path = item.path
                    raw_content = item.content
                elif isinstance(item, dict):
                    if "path" not in item or "content" not in item:
                        raise ValueError(f"Invalid file entry under '{key}': {item}")
                    raw_path = item["path"]
                    raw_content = item["content"]
                else:
                    raise ValueError(
                        f"Each file entry must be FileSpec or dict with 'path' and 'content', got {type(item)}"
                    )

                path_str = str(raw_path)
                path = render_template(path_str, context)
                files_to_write.append({"path": path, "content": raw_content})

        else:
            raise ValueError("Either 'files' or 'files_key' must be provided in WriteFilesConfig.")

        # Write each file to disk
        for entry in files_to_write:
            rel_path: str = entry.get("path", "")
            content = entry.get("content")

            # Compute the final filesystem path
            if root:
                combined = os.path.join(root, rel_path)
            else:
                combined = rel_path
            final_path = os.path.normpath(combined)

            try:
                # Ensure parent directories exist
                parent_dir = os.path.dirname(final_path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)

                # Serialize content if needed
                if isinstance(content, (dict, list)):
                    try:
                        text = json.dumps(content, ensure_ascii=False, indent=2)
                    except Exception as err:
                        raise ValueError(
                            f"Failed to serialize content for '{final_path}': {err}"
                        )
                else:
                    # Convert None to empty string, others to string if not already
                    if content is None:
                        text = ""
                    elif not isinstance(content, str):
                        text = str(content)
                    else:
                        text = content

                # Debug log before writing
                self.logger.debug(f"[WriteFilesStep] Writing file: {final_path}\nContent:\n{text}")

                # Write file using UTF-8 encoding
                with open(final_path, "w", encoding="utf-8") as f:
                    f.write(text)

                # Info log after successful write
                size = len(text.encode("utf-8"))
                self.logger.info(f"[WriteFilesStep] Wrote file: {final_path} ({size} bytes)")

            except Exception as exc:
                self.logger.error(f"[WriteFilesStep] Error writing file '{rel_path}': {exc}")
                raise
