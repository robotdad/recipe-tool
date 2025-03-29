# __init__.py

from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.generate_llm import GenerateWithLLMStep
from recipe_executor.steps.read_file import ReadFileStep
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.write_files import WriteFileStep

# Explicitly populate the registry
STEP_REGISTRY.update({
    "read_file": ReadFileStep,
    "write_file": WriteFileStep,
    "generate": GenerateWithLLMStep,
    "execute_recipe": ExecuteRecipeStep,
})
