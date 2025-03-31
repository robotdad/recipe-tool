from typing import Dict, List, Optional

from pydantic import BaseModel, validator
from pydantic_settings import BaseSettings


class FileSpec(BaseModel):
    """Represents a single file to be generated.

    Attributes:
        path (str): Relative path where the file should be written.
        content (str): The content of the file.
    """
    path: str
    content: str


class FileGenerationResult(BaseModel):
    """Result of an LLM file generation request.

    Attributes:
        files (List[FileSpec]): List of files to generate.
        commentary (Optional[str]): Optional commentary from the LLM.
    """
    files: List[FileSpec]
    commentary: Optional[str] = None


class ReadFileConfig(BaseModel):
    """Configuration for a ReadFile step.

    Attributes:
        file_path (str): The path of the file to read.
        store_key (str): Key under which to store the file content. Defaults to "spec".
    """
    file_path: str
    store_key: str = "spec"


class GenerateCodeConfig(BaseModel):
    """Configuration for a GenerateCode step.

    Attributes:
        input_key (str): Key in context where the specification is stored. Defaults to "spec".
        output_key (str): Key to store the generated code result. Defaults to "codegen_result".
    """
    input_key: str = "spec"
    output_key: str = "codegen_result"


class WriteFileConfig(BaseModel):
    """Configuration for a WriteFile step.

    Attributes:
        input_key (str): Key in context where the codegen result is stored. Defaults to "codegen_result".
        output_root (str): Root directory where files will be written.
    """
    input_key: str = "codegen_result"
    output_root: str


class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type (str): The type of the recipe step.
        config (Dict): Dictionary containing configuration for the step.
    """
    type: str
    config: Dict


class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """
    steps: List[RecipeStep]


class AzureOpenAISettings(BaseSettings):
    """Configuration model for Azure OpenAI services.

    Attributes:
        endpoint (str): The Azure OpenAI endpoint URL.
        use_managed_identity (bool): Flag indicating if managed identity authentication is used. Defaults to False.
        api_key (Optional[str]): API key for authentication when not using managed identity.
    """
    endpoint: str
    use_managed_identity: bool = False
    api_key: Optional[str] = None

    @validator("api_key", always=True)
    def validate_authentication(cls, v, values):
        """
        Validates that an API key is provided when managed identity is not used.
        
        Raises:
            ValueError: If API key is not provided and managed identity is disabled.
        """
        use_managed_identity = values.get("use_managed_identity", False)
        if not use_managed_identity and not v:
            raise ValueError("API key must be provided when use_managed_identity is False")
        return v
