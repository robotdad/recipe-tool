repo_root = $(shell git rev-parse --show-toplevel)
include $(repo_root)/tools/makefiles/python.mk

.PHONY: run

# Run the Gradio app
run:
	@echo "Starting Recipe Executor Gradio app..."
	@uv run python -m recipe_executor_app.app --host 127.0.0.1