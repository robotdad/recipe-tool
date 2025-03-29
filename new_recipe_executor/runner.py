import json
import os
import re
from executor import Executor
from context import Context
from models import Recipe


def load_recipe(recipe_path: str) -> Recipe:
    # Read the markdown file and extract the JSON array of steps
    with open(recipe_path, 'r') as f:
        content = f.read()
    # A simple regex to extract the JSON block (assuming it's the first JSON block in the file)
    match = re.search(r'\[.*\]', content, re.DOTALL)
    if not match:
        raise ValueError('No JSON array of steps found in the recipe file.')
    recipe_json = match.group(0)
    recipe_data = json.loads(recipe_json)
    return Recipe(steps=recipe_data)


def run_recipe(recipe_path: str, output_root: str, log_dir: str, logger) -> None:
    # Set up the execution context
    context = Context(
        input_root=os.path.dirname(recipe_path),
        output_root=output_root,
        extras={}
    )

    recipe = load_recipe(recipe_path)
    executor = Executor(recipe=recipe, context=context, logger=logger)
    executor.execute_all()
