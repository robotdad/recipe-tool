import logging
import os
from typing import Any, Dict, List, Optional

from recipe_executor.models import FileSpec
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Fields:
        files_key: Optional name of the context key holding a List[FileSpec].
        files: Optional list of dictionaries with 'path' and 'content' keys.
        root: Optional base path to prepend to all output file paths.
    """

    files_key: Optional[str] = None
    files: Optional[List[Dict[str, Any]]] = None
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, WriteFilesConfig(**config))

    async def execute(self, context) -> None:
        files_to_write: List[FileSpec] = []
        # Prefer files in config, fallback to files_key in context
        if self.config.files is not None:
            files_to_write = self._resolve_files_from_config(self.config.files, context)
        elif self.config.files_key is not None:
            if self.config.files_key not in context:
                msg = f"WriteFilesStep: Key '{self.config.files_key}' not found in context."
                self.logger.error(msg)
                raise ValueError(msg)
            artifact = context[self.config.files_key]
            files_to_write = self._normalize_files_from_context(artifact)
        else:
            msg = "WriteFilesStep: Either 'files' or 'files_key' must be provided in config."
            self.logger.error(msg)
            raise ValueError(msg)

        if not files_to_write:
            msg = "WriteFilesStep: No files to write."
            self.logger.warning(msg)
            return

        for file_spec in files_to_write:
            try:
                # Render root and path using templates
                rendered_root = render_template(self.config.root, context) if self.config.root else "."
                rendered_path = render_template(file_spec.path, context)
                output_path = os.path.normpath(os.path.join(rendered_root, rendered_path))
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                # Log file info (debug) before writing
                self.logger.debug(f"WriteFilesStep: Preparing to write file: {output_path}")
                self.logger.debug(f"WriteFilesStep: File content for {output_path}: {repr(file_spec.content)}")
                # Write content as utf-8 (or dump content as-is if not string)
                with open(output_path, "w", encoding="utf-8") as f:
                    if isinstance(file_spec.content, str):
                        f.write(file_spec.content)
                    else:
                        import json

                        f.write(json.dumps(file_spec.content, indent=2))

                size = len(file_spec.content) if isinstance(file_spec.content, str) else len(str(file_spec.content))
                self.logger.info(f"WriteFilesStep: Wrote file '{output_path}' ({size} bytes)")
            except Exception as ex:
                self.logger.error(f"WriteFilesStep: Failed to write file '{file_spec.path}': {str(ex)}")
                raise

    def _resolve_files_from_config(self, files_config: List[Dict[str, Any]], context) -> List[FileSpec]:
        files: List[FileSpec] = []
        for idx, file_dict in enumerate(files_config):
            # Determine the path
            path: Optional[str] = None
            if "path" in file_dict:
                path = file_dict["path"]
                if path is None:
                    raise ValueError(f"WriteFilesStep: 'path' cannot be None (file index {idx})")
                path = render_template(path, context)
            elif "path_key" in file_dict:
                key = file_dict["path_key"]
                if key not in context:
                    raise ValueError(f"WriteFilesStep: path_key '{key}' not in context (file index {idx})")
                path = str(context[key])
                path = render_template(path, context)
            else:
                raise ValueError(f"WriteFilesStep: File at index {idx} missing 'path' or 'path_key'.")
            # Determine the content
            content: Any = None
            if "content" in file_dict:
                content = file_dict["content"]
            elif "content_key" in file_dict:
                key = file_dict["content_key"]
                if key not in context:
                    raise ValueError(f"WriteFilesStep: content_key '{key}' not in context (file index {idx})")
                content = context[key]
            else:
                raise ValueError(f"WriteFilesStep: File at index {idx} missing 'content' or 'content_key'.")
            files.append(FileSpec(path=path, content=content))
        return files

    def _normalize_files_from_context(self, artifact: Any) -> List[FileSpec]:
        if isinstance(artifact, FileSpec):
            return [artifact]
        elif isinstance(artifact, list):
            files: List[FileSpec] = []
            for idx, item in enumerate(artifact):
                if isinstance(item, FileSpec):
                    files.append(item)
                elif isinstance(item, dict):
                    try:
                        files.append(FileSpec.model_validate(item))
                    except Exception as ex:
                        raise ValueError(f"WriteFilesStep: Invalid file dict at index {idx}: {ex}")
                else:
                    raise ValueError(f"WriteFilesStep: Invalid file type at index {idx}")
            return files
        elif isinstance(artifact, dict):
            # Try to coerce to FileSpec
            try:
                return [FileSpec.model_validate(artifact)]
            except Exception as ex:
                raise ValueError(f"WriteFilesStep: Invalid file dict in context: {ex}")
        else:
            raise ValueError("WriteFilesStep: Provided artifact is not a FileSpec, list, or dict.")
