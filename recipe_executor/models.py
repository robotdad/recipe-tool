from typing import List, Optional

from pydantic import BaseModel


class ReadFileConfig(BaseModel):
    file_path: str
    store_key: str = "spec"  # Key under which to store the file content


class GenerateCodeConfig(BaseModel):
    input_key: str = "spec"  # Key in context where the specification is stored
    output_key: str = "codegen_result"  # Key to store the generated code result


class WriteFileConfig(BaseModel):
    input_key: str = "codegen_result"  # Key in context where the codegen result is stored
    output_root: str  # Root directory where files will be written


class FileSpec(BaseModel):
    path: str
    content: str


class CodeGenResult(BaseModel):
    files: List[FileSpec]
    commentary: Optional[str] = None


class RecipeStep(BaseModel):
    type: str
    config: dict


class Recipe(BaseModel):
    steps: List[RecipeStep]
