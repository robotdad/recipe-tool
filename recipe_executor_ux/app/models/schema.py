from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class RecipeMetadata(BaseModel):
    """Metadata for a recipe."""
    id: str
    name: str
    path: str
    description: Optional[str] = ""
    step_count: int

class RecipeList(BaseModel):
    """List of recipe metadata."""
    recipes: List[RecipeMetadata]

class ExecutionRequest(BaseModel):
    """Request to execute a recipe."""
    recipe_path: str
    context_vars: Dict[str, str] = {}

class ExecutionResponse(BaseModel):
    """Response from executing a recipe."""
    execution_id: str

class SaveRecipeRequest(BaseModel):
    """Request to save a recipe."""
    path: str
    steps: List[Dict[str, Any]]
    description: Optional[str] = None

class SaveRecipeResponse(BaseModel):
    """Response from saving a recipe."""
    success: bool
    path: str
    error: Optional[str] = None
