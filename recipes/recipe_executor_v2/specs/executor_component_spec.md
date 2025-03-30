# Executor Component Specification

## Purpose

The Executor component is responsible for loading recipe definitions from various sources and executing their steps sequentially. It serves as the central orchestration mechanism for the Recipe Executor system.

## Core Requirements

The Executor component should:

1. Load recipes from multiple input types (file paths, JSON strings, dictionaries)
2. Extract and validate recipe steps
3. Execute steps in sequence using their type to instantiate the correct step class
4. Handle errors gracefully with appropriate logging
5. Support extraction of JSON from markdown fenced code blocks
6. Follow a minimal design approach with clear error messages

## Component Structure

The Executor component should consist of a single `RecipeExecutor` class:

```python
class RecipeExecutor:
    """
    Unified executor that loads a recipe (from a file path, JSON string, or dict),
    and executes its steps sequentially using the provided context.
    """

    def execute(self, recipe, context: Context, logger: Optional[logging.Logger] = None) -> None:
        """
        Execute a recipe with the given context.

        Args:
            recipe: Recipe to execute, can be a file path, JSON string, or dict
            context: Context instance to use for execution
            logger: Optional logger to use, creates a default one if not provided

        Raises:
            ValueError: If recipe format is invalid or step execution fails
            TypeError: If recipe type is not supported
        """
```

## Recipe Loading Logic

The Executor should handle the following input types:

1. File paths:

   - Read the file content
   - Check for JSON fenced code blocks (`json ... `)
   - If found, extract and parse the JSON from the block
   - If not found, try to parse the entire file as JSON

2. JSON strings:

   - Parse the string as JSON

3. Dictionaries:
   - Use directly as a recipe

After loading, the Executor should:

- Check for a 'steps' key if the loaded data is a dict
- Otherwise, assume the loaded data itself is the steps list
- Validate that steps is a list of dictionaries

## Step Execution Logic

For each step in the recipe:

1. Validate the step is a dictionary with a 'type' field
2. Look up the step class in the STEP_REGISTRY using the 'type' field
3. Instantiate the step class with the step configuration and logger
4. Execute the step with the provided context
5. Continue to the next step or handle any errors

## Error Handling

The Executor should provide clear error messages for:

- Invalid recipe format or structure
- Missing or unknown step types
- Errors during step execution (with appropriate traceback)

## Integration Points

The Executor component integrates with:

1. **Context**: Passed to each step for data sharing
2. **Step Registry**: Used to look up step classes by type
3. **Logger**: For providing execution status and error information

## Future Considerations

1. Parallel step execution
2. Conditional branching between steps
3. Step retry policies
4. Progress tracking and reporting
