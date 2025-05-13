from fastapi import APIRouter, File, Form, HTTPException, UploadFile
import json
import logging
from pathlib import Path
from typing import Dict, Any

from app.models.schema import RecipeList, SaveRecipeResponse

router = APIRouter(prefix="/api/recipes", tags=["recipes"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=RecipeList)
async def list_recipes(directory: str = "recipes"):
    """List all available recipes with metadata."""
    logger.debug(f"Listing recipes in directory: {directory}")
    recipes = []
    try:
        for path in Path(directory).glob("**/*.json"):
            if path.is_file():
                # Parse the JSON to extract metadata
                try:
                    with open(path, "r") as f:
                        content = json.load(f)

                    # Extract basic info
                    name = path.stem
                    description = content.get("description", "")
                    step_count = len(content.get("steps", []))

                    recipes.append({
                        "id": str(path),
                        "name": name,
                        "path": str(path),
                        "description": description,
                        "step_count": step_count
                    })
                except json.JSONDecodeError:
                    logger.warning(f"Skipping invalid JSON file: {path}")
                    continue
                except Exception as e:
                    logger.warning(f"Error processing recipe {path}: {str(e)}")
                    continue
    except Exception as e:
        logger.error(f"Error listing recipes: {str(e)}")
        return {"recipes": []}

    logger.debug(f"Found {len(recipes)} recipes")
    return {"recipes": recipes}

@router.get("/{recipe_id:path}")
async def get_recipe(recipe_id: str):
    """Get full recipe JSON by ID."""
    logger.debug(f"Getting recipe: {recipe_id}")
    try:
        # Ensure we're dealing with a proper path
        path = Path(recipe_id)
        logger.debug(f"Checking path: {path} (absolute: {path.absolute()})")

        if not path.exists():
            # Try with base directory if not found directly
            cwd = Path.cwd()
            logger.debug(f"Current working directory: {cwd}")

            # Try removing 'recipes/' prefix if it's duplicated
            if recipe_id.startswith('recipes/') and cwd.name == 'recipes':
                alternative_path = Path(recipe_id[8:])  # Remove 'recipes/'
                logger.debug(f"Trying alternative path: {alternative_path}")
                if alternative_path.exists():
                    path = alternative_path

            # If still not found, try as relative path from cwd
            if not path.exists():
                logger.warning(f"Recipe not found at: {path}")
                raise HTTPException(status_code=404, detail=f"Recipe not found: {recipe_id}")

        logger.debug(f"Reading recipe from: {path}")
        with open(path, "r") as f:
            content = json.load(f)

        logger.debug(f"Successfully loaded recipe: {recipe_id}")
        return content
    except HTTPException:
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in recipe file: {recipe_id}")
        raise HTTPException(status_code=400, detail="Invalid JSON in recipe file")
    except Exception as e:
        logger.error(f"Error getting recipe {recipe_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save", response_model=SaveRecipeResponse)
async def save_recipe(recipe: Dict[str, Any]):
    """Save recipe JSON to file."""
    logger.debug(f"Saving recipe to: {recipe.get('path')}")
    try:
        path = recipe.get("path")
        if not path:
            logger.warning("No path specified for recipe save")
            raise HTTPException(status_code=400, detail="No path specified")

        # Ensure directory exists
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Clean recipe data - remove any empty values
        cleaned_recipe = clean_recipe_data(recipe)

        # Save the recipe
        with open(path, "w") as f:
            json.dump(cleaned_recipe, f, indent=2)

        logger.info(f"Recipe saved successfully to {path}")
        return {"success": True, "path": path}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving recipe: {str(e)}")
        return {"success": False, "path": recipe.get("path", ""), "error": str(e)}

def clean_recipe_data(recipe: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean recipe data by removing empty string values, null values, etc.
    Recursively processes nested dictionaries and lists.
    """
    if not isinstance(recipe, dict):
        return recipe

    result = {}
    for key, value in recipe.items():
        # Skip empty strings, None values
        if value == "" or value is None:
            continue

        # Handle dictionaries recursively
        if isinstance(value, dict):
            cleaned = clean_recipe_data(value)
            if cleaned:  # Only add non-empty dicts
                result[key] = cleaned
        # Handle lists recursively
        elif isinstance(value, list):
            cleaned_list = []
            for item in value:
                if isinstance(item, dict):
                    cleaned_item = clean_recipe_data(item)
                    if cleaned_item:  # Only add non-empty dicts
                        cleaned_list.append(cleaned_item)
                elif item != "" and item is not None:  # Skip empty strings and None values
                    cleaned_list.append(item)
            if cleaned_list:  # Only add non-empty lists
                result[key] = cleaned_list
        else:
            result[key] = value

    return result

@router.post("/upload")
async def upload_recipe(
    file: UploadFile = File(...),
    directory: str = Form("recipes")
):
    """Upload a JSON recipe file."""
    logger.info(f"Uploading recipe file: {file.filename}")

    try:
        # Ensure we have a valid filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        # Ensure the file has a .json extension
        if not file.filename.lower().endswith('.json'):
            raise HTTPException(status_code=400, detail="File must have .json extension")

        # Create directory if needed
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)

        # Create the destination path
        file_path = dir_path / file.filename

        # Check if file exists
        if file_path.exists():
            logger.warning(f"File already exists: {file_path}")
            # Use a simple numbering scheme for duplicate files
            base_name = file_path.stem
            extension = file_path.suffix
            counter = 1
            while file_path.exists():
                file_path = dir_path / f"{base_name}_{counter}{extension}"
                counter += 1

        # Read and validate the JSON content
        content = await file.read()
        try:
            recipe_json = json.loads(content)

            # Basic validation - check if it has steps
            if not isinstance(recipe_json, dict):
                raise HTTPException(status_code=400, detail="JSON must be an object")

            if "steps" not in recipe_json or not isinstance(recipe_json["steps"], list):
                raise HTTPException(status_code=400, detail="Recipe must have a steps array")

            # Clean the recipe data
            cleaned_recipe = clean_recipe_data(recipe_json)

            # Make sure the path field is set correctly
            cleaned_recipe["path"] = str(file_path)

            # Write the cleaned JSON to file
            with open(file_path, "w") as f:
                json.dump(cleaned_recipe, f, indent=2)

            logger.info(f"Recipe file uploaded and saved to: {file_path}")
            return {
                "success": True,
                "filename": file.filename,
                "path": str(file_path),
                "recipe": cleaned_recipe
            }

        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON content")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
    finally:
        await file.close()
