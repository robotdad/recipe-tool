repo_root = $(shell git rev-parse --show-toplevel)
include $(repo_root)/tools/makefiles/python.mk

# Document Generator specific targets
.PHONY: refresh-examples
refresh-examples:  ## Refresh example docpacks from source JSON files
	python scripts/refresh_examples.py
