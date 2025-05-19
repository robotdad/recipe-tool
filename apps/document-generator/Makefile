repo_root = $(shell git rev-parse --show-toplevel)
include $(repo_root)/tools/makefiles/python.mk

.PHONY: run

# Run the Gradio app
run:
	@echo "Starting Document Generator Gradio app..."
	@uv run python -m document_generator.main
