from typing import List, Dict, Optional
from pydantic import BaseModel


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


class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        name (Optional[str]): The name of the step.
        description (Optional[str]): A brief description of the step.
        type (str): The type of the recipe step.
        config (Dict): Dictionary containing configuration for the step.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    type: str
    config: Dict


class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        name (str): The name of the recipe.
        description (Optional[str]): A brief description of the recipe.
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """
    name: str
    description: Optional[str] = None
    steps: List[RecipeStep]
