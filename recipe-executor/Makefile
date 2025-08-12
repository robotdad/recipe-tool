repo_root = $(shell git rev-parse --show-toplevel)
include $(repo_root)/tools/makefiles/python.mk

# Project-specific test coverage
PYTEST_ARGS += --cov=recipe_executor

.PHONY: recipe-executor-create recipe-executor-edit create-component edit-component

# Create recipe executor code from scratch using modular recipes
recipe-executor-create:
	@echo "Generating recipe executor code from modular recipes..."
	cd $(repo_root) && recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json model=openai/o4-mini existing_code_root=recipe-executor/recipe_executor

# Edit existing recipe executor code using modular recipes
recipe-executor-edit:
	@echo "Editing recipe executor code from modular recipes..."
	cd $(repo_root) && recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json model=openai/o4-mini edit=true existing_code_root=recipe-executor/recipe_executor

# Create a specific component
create-component:
	@echo "Generating component $(COMPONENT)..."
	cd $(repo_root) && recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json model=openai/o4-mini component_id=$(COMPONENT) existing_code_root=recipe-executor/recipe_executor

# Edit a specific component
edit-component:
	@echo "Editing component $(COMPONENT)..."
	cd $(repo_root) && recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json model=openai/o4-mini component_id=$(COMPONENT) edit=true existing_code_root=recipe-executor/recipe_executor

# Usage examples:
# make create-component COMPONENT=context
# make edit-component COMPONENT=llm_utils.llm
