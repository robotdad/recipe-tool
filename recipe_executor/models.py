from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class FileSpec(BaseModel):
    """
    Represents a single file to be generated.

    Attributes:
        path (str): Relative path where the file should be written.
        content (str): The content of the file.
    """
    path: str
    content: str


class FileGenerationResult(BaseModel):
    """
    Result of an LLM file generation request.

    Attributes:
        files (List[FileSpec]): List of files to generate.
        commentary (Optional[str]): Optional commentary from the LLM.
    """
    files: List[FileSpec]
    commentary: Optional[str] = None


class ReadFileConfig(BaseModel):
    """
    Configuration for a ReadFile step.

    Attributes:
        file_path (str): The path of the file to read.
        store_key (str): Key under which to store the file content. Defaults to "spec".
    """
    file_path: str
    store_key: str = "spec"


class GenerateCodeConfig(BaseModel):
    """
    Configuration for a GenerateCode step.

    Attributes:
        input_key (str): Key in context where the specification is stored. Defaults to "spec".
        output_key (str): Key to store the generated code result. Defaults to "codegen_result".
    """
    input_key: str = "spec"
    output_key: str = "codegen_result"


class WriteFileConfig(BaseModel):
    """
    Configuration for a WriteFile step.

    Attributes:
        input_key (str): Key in context where the codegen result is stored. Defaults to "codegen_result".
        output_root (str): Root directory where files will be written.
    """
    input_key: str = "codegen_result"
    output_root: str


class RecipeStep(BaseModel):
    """
    A single step in a recipe.

    Attributes:
        type (str): The type of the recipe step.
        config (Dict): Dictionary containing configuration for the step.
    """
    type: str
    config: Dict


class Recipe(BaseModel):
    """
    A complete recipe with multiple steps.

    Attributes:
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """
    steps: List[RecipeStep]


class AzureOpenAISettings(BaseSettings):
    """
    Configuration model for Azure OpenAI services.

    This model supports configuring Azure OpenAI using either an API key or managed identity.

    Attributes:
        endpoint (str): The Azure OpenAI endpoint URL, mapped from environment variable AZURE_OPENAI_ENDPOINT.
        openai_api_version (str): API version to use, mapped from environment variable OPENAI_API_VERSION.
        api_key (Optional[str]): API key for authentication when not using managed identity, mapped from AZURE_OPENAI_API_KEY.
        use_managed_identity (bool): Flag for managed identity auth, defaults to False, mapped from AZURE_USE_MANAGED_IDENTITY.
        managed_identity_client_id (Optional[str]): Specific managed identity client ID, mapped from AZURE_MANAGED_IDENTITY_CLIENT_ID.
    """
    endpoint: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    openai_api_version: str = Field(..., env="OPENAI_API_VERSION")
    api_key: Optional[str] = Field(None, env="AZURE_OPENAI_API_KEY")
    use_managed_identity: bool = Field(False, env="AZURE_USE_MANAGED_IDENTITY")
    managed_identity_client_id: Optional[str] = Field(None, env="AZURE_MANAGED_IDENTITY_CLIENT_ID")

    @validator('api_key', always=True)
    def validate_authentication(cls, v, values):
        """
        Validates that either an API key is provided or managed identity is enabled.

        Raises:
            ValueError: If API key is not provided when managed identity is not used.
        """
        use_managed_identity = values.get('use_managed_identity', False)
        if not use_managed_identity and not v:
            raise ValueError("Authentication configuration error: API key must be provided when managed identity is not used.")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
