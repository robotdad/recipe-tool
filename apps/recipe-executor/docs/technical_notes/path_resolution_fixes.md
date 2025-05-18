# Path Resolution Fixes

This document details the path resolution fixes implemented in the Recipe Executor App to address issues with finding files in the repository structure.

## Overview

The Recipe Executor App relies on various file paths to load resources such as recipes, examples, and templates. Due to the nested directory structure and different entry points, resolving these paths correctly can be challenging.

## Issues Addressed

### 1. Recipe Creator Path Resolution

**Problem**: The app was failing to find the recipe creator recipe at `../../recipes/recipe_creator/create.json`, resulting in error messages like:
```
Recipe creator recipe not found: /home/brkrabac/repos/recipes/recipe_creator/create.json
```

**Root Cause**: The path in the configuration was incorrect relative to the module location, and the path resolution logic didn't account for the nested structure of the repository.

**Solution**:
1. Updated the path in the configuration to use the correct relative path:
   ```python
   recipe_creator_path: str = "../../../recipes/recipe_creator/create.json"
   ```

2. Implemented a robust fallback mechanism:
   ```python
   # Try main path first
   creator_recipe_path = os.path.join(os.path.dirname(__file__), settings.recipe_creator_path)
   creator_recipe_path = os.path.normpath(creator_recipe_path)
   
   # If not found, try fallback approach
   if not os.path.exists(creator_recipe_path):
       repo_root = get_repo_root()
       fallback_path = os.path.join(repo_root, "recipes/recipe_creator/create.json")
       if os.path.exists(fallback_path):
           creator_recipe_path = fallback_path
   ```

### 2. Example Recipe Loading

**Problem**: Example recipes couldn't be loaded, with errors like:
```
Error loading example: [Errno 2] No such file or directory: '/home/brkrabac/recipes/example_simple/test_recipe.json'
```

**Root Cause**: The example paths in the configuration were being resolved incorrectly, and the app wasn't accounting for the various ways these paths might need to be interpreted based on the directory structure.

**Solution**: Implemented a multi-strategy approach to find example files:

```python
repo_root = get_repo_root()
recipe_root = os.path.join(repo_root, "recipes")
potential_paths = [
    # 1. Direct interpretation of the path
    example_path,
    
    # 2. Relative to repo root
    os.path.join(repo_root, example_path.lstrip("../")),
    
    # 3. Relative to recipe_root (replacing initial ../../recipes with recipe_root)
    os.path.join(recipe_root, example_path.replace("../../recipes/", "")),
    
    # 4. Relative to recipe_root (replacing initial ../../../recipes with recipe_root)
    os.path.join(recipe_root, example_path.replace("../../../recipes/", "")),
    
    # 5. Direct path in recipes directory
    os.path.join(recipe_root, os.path.basename(example_path))
]

# Try each path until we find one that exists
full_path = None
for path in potential_paths:
    if os.path.exists(path):
        full_path = path
        logger.info(f"Found example at: {full_path}")
        break
```

This approach tries multiple potential locations for the file, providing clear debug information when issues arise.

### 3. Context Paths

**Problem**: The context variables for `recipe_root`, `ai_context_root`, and `output_root` might not be resolved correctly in different situations.

**Solution**: Enhanced context preparation with detailed logging:

```python
# Log important paths to help with debugging
logger.info(f"Recipe Executor paths:")
logger.info(f"  - Current working directory: {os.getcwd()}")
logger.info(f"  - Repository root: {get_repo_root()}")
logger.info(f"  - Context paths:")
logger.info(f"    - recipe_root: {context.dict().get('recipe_root', 'Not set')}")
logger.info(f"    - ai_context_root: {context.dict().get('ai_context_root', 'Not set')}")
logger.info(f"    - output_root: {context.dict().get('output_root', 'Not set')}")
```

## General Path Resolution Improvements

### 1. Enhanced Logging

Added detailed logging of paths at key points to aid in debugging:
- Original paths being used
- Attempts to resolve paths
- Successful path resolution
- Failed path resolution with details of what was tried

### 2. Fallback Mechanisms

Implemented fallback mechanisms for critical paths:
- If the first path resolution approach fails, try alternative approaches
- Test multiple potential paths for required files
- Provide clear error messages when all attempts fail

### 3. Robust Path Handling

Improved path handling functions to better deal with different path formats:
- Absolute paths
- Relative paths with `../` components
- Paths relative to specific roots (repo root, recipe root, etc.)
- Paths with different formats (e.g., with or without leading `/`)

## Testing

These path resolution fixes have been tested in the following scenarios:
1. Running the app from different working directories
2. Loading examples from the Examples tab
3. Creating recipes with the recipe creator
4. Executing recipes from different locations

## Future Improvements

For further robustness, consider:
1. Centralizing all path resolution in a dedicated module
2. Adding unit tests specifically for path resolution
3. Implementing a path cache to avoid repeated path resolution operations
4. Providing clearer user feedback when paths cannot be resolved