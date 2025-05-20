repo_root = $(shell git rev-parse --show-toplevel)
include $(repo_root)/tools/makefiles/python.mk

.PHONY: run

# Run the Gradio app
run:
	@echo "Starting Recipe Tool Gradio app..."
	@uv run python -m recipe_tool_app.app
