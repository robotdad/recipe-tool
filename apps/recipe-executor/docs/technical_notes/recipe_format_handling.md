# Recipe Format Handling

## Issue

The Recipe Executor app was encountering an issue where recipes were being successfully created (as evidenced by files in the `output` directory) but not showing in the UI. The problem was in how the application processes the `generated_recipe` field in the context object after recipe creation.

## Context Structure

When a recipe is created, the context object includes a `generated_recipe` field, which has a specific structure:

```json
{
  "generated_recipe": [
    {
      "path": "analyze_codebase.json",
      "content": "{\"steps\": [{\"type\": \"read_files\", ...}]}"
    }
  ]
}
```

This structure comes from the recipe generator's output format, which follows the pattern of a list of file objects, where each file object has a `path` and `content` property.

## Implementation Changes

The original code was only handling one specific format for the `generated_recipe` field. The solution was to enhance the code to handle multiple possible formats:

1. **List with dictionary items** (the most common format):
   ```python
   if isinstance(generated_recipe, list) and len(generated_recipe) > 0:
       item = generated_recipe[0]
       if isinstance(item, dict) and "content" in item:
           output_recipe = item["content"]
   ```

2. **Direct string content**:
   ```python
   elif isinstance(generated_recipe, str):
       output_recipe = generated_recipe
   ```

3. **Dictionary with content**:
   ```python
   elif isinstance(generated_recipe, dict) and "content" in generated_recipe:
       output_recipe = generated_recipe["content"]
   ```

## Additional Safeguards

We also added several safeguards to ensure reliable recipe processing:

1. **Type conversion** for non-string content:
   ```python
   if not isinstance(output_recipe, str):
       if isinstance(output_recipe, (dict, list)):
           output_recipe = json.dumps(output_recipe, indent=2)
       else:
           output_recipe = str(output_recipe)
   ```

2. **Enhanced error handling** with detailed logging:
   ```python
   except (json.JSONDecodeError, TypeError) as e:
       logger.error(f"Error parsing recipe JSON: {e}")
       logger.error(f"Recipe content causing error: {output_recipe[:500]}...")
   ```

3. **File finding logic** to look for recently created files as a fallback:
   ```python
   if os.path.exists(output_root):
       json_files = [f for f in os.listdir(output_root) if f.endswith(".json")]
       if json_files:
           json_files_with_paths = [os.path.join(output_root, f) for f in json_files]
           newest_file = max(json_files_with_paths, key=os.path.getmtime)
           
           # Only use if created in the last 30 seconds
           if time.time() - os.path.getmtime(newest_file) < 30:
               # Read this file
   ```

## Debugging

For debugging purposes, we've added:

1. Extensive logging at DEBUG level to track the recipe data flow
2. A "Debug Context" tab in the UI that shows the full context object
3. Detailed error messages that include the actual error and recipe content causing the issue

## Testing the Fix

To test if the fix resolves the issue:

1. Set logger to DEBUG level (already implemented)
2. Run the application
3. Create a recipe using the "Create Recipe" tab
4. Check if the recipe appears in the UI
5. If it doesn't, examine the logs and the Debug Context tab for clues

## Known Edge Cases

1. **Deeply nested recipe structures**: Some complex recipes might have deeply nested structures that require special handling
2. **Non-JSON content**: If the recipe content isn't valid JSON, it will be displayed as is but won't be parsed for the preview
3. **Recipe files outside the project**: If recipes are created outside the expected directories, the fallback file finding logic might not locate them