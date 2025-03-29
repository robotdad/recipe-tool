from pydantic import BaseModel
from typing import List, Optional, Any


class FileSpec(BaseModel):
    path: str
    content: str


class CodeGenResult(BaseModel):
    files: List[FileSpec]
    commentary: Optional[str] = None


class ReadFileConfig(BaseModel):
    file_path: str
    store_key: str


class GenerateCodeConfig(BaseModel):
    input_key: str
    output_key: str
    spec: str


class WriteFileConfig(BaseModel):
    input_key: str
    output_root: Optional[str] = None


class Recipe(BaseModel):
    # Steps is a list of arbitrary dictionaries; each should have a 'type' and 'config'
    steps: List[Any]
