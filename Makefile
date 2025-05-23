# Recipe Tool Workspace Makefile
# ================================

# Variables
SHELL := /bin/bash
repo_root := $(shell pwd)
uv := uv

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

# ================================
# Setup and Installation
# ================================

.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)Recipe Tool Workspace$(NC)"
	@echo "====================="
	@echo ""
	@echo "$(YELLOW)Setup:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {if ($$1 ~ /^(install|sync|clean|ai-context-files)$$/) printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {if ($$1 ~ /^(test|lint|format|check|run)/) printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Building:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {if ($$1 ~ /^(build|publish)/) printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Individual Packages:$(NC)"
	@echo "  $(GREEN)test-<package>$(NC)       Test specific package (e.g., make test-recipe-tool)"
	@echo "  $(GREEN)build-<package>$(NC)      Build specific package"
	@echo ""
	@echo "$(YELLOW)Package Names:$(NC) recipe-executor, recipe-tool, document-generator-app,"
	@echo "               recipe-executor-app, recipe-tool-app, python-code-tools,"
	@echo "               recipe-tool-mcp-server"

.PHONY: install
install: sync ## Alias for sync (for backwards compatibility)

.PHONY: sync
sync: ## Install/update all workspace dependencies
	@echo "$(BLUE)🔄 Syncing workspace dependencies...$(NC)"
	$(uv) sync --group dev
	@echo "$(GREEN)✅ Workspace synchronized$(NC)"

.PHONY: sync-minimal
sync-minimal: ## Install only production dependencies
	@echo "$(BLUE)🔄 Syncing minimal dependencies...$(NC)"
	$(uv) sync
	@echo "$(GREEN)✅ Minimal sync complete$(NC)"

# ================================
# AI Context Files
# ================================

.PHONY: ai-context-files
ai-context-files: ## Build AI context files for development
	@echo "$(BLUE)🤖 Building AI context files...$(NC)"
	@$(uv) run python $(repo_root)/tools/build_ai_context_files.py
	@$(uv) run python $(repo_root)/tools/build_git_collector_files.py
	@echo "$(GREEN)✅ AI context files generated$(NC)"

# ================================
# Testing
# ================================

.PHONY: test
test: ## Run all tests
	@echo "$(BLUE)🧪 Running all tests...$(NC)"
	$(uv) run pytest --no-cov
	@echo "$(GREEN)✅ All tests completed$(NC)"

.PHONY: test-verbose
test-verbose: ## Run all tests with verbose output
	@echo "$(BLUE)🧪 Running all tests (verbose)...$(NC)"
	$(uv) run pytest --no-cov -v

.PHONY: test-core
test-core: ## Test only core libraries (recipe-executor, recipe-tool)
	@echo "$(BLUE)🧪 Testing core libraries...$(NC)"
	$(uv) run pytest recipe-executor/ recipe-tool/ --no-cov

.PHONY: test-apps
test-apps: ## Test only apps
	@echo "$(BLUE)🧪 Testing apps...$(NC)"
	$(uv) run pytest apps/ --no-cov

.PHONY: test-mcp
test-mcp: ## Test only MCP servers
	@echo "$(BLUE)🧪 Testing MCP servers...$(NC)"
	$(uv) run pytest mcp-servers/ --no-cov

.PHONY: test-coverage
test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)🧪 Running tests with coverage...$(NC)"
	$(uv) run pytest --cov=recipe_executor --cov=recipe_tool --cov-report=html --cov-report=term

# Individual package testing
.PHONY: test-recipe-executor
test-recipe-executor: ## Test recipe-executor package
	@echo "$(BLUE)🧪 Testing recipe-executor...$(NC)"
	$(uv) run --package recipe-executor pytest

.PHONY: test-recipe-tool
test-recipe-tool: ## Test recipe-tool package
	@echo "$(BLUE)🧪 Testing recipe-tool...$(NC)"
	$(uv) run --package recipe-tool pytest

.PHONY: test-document-generator-app
test-document-generator-app: ## Test document-generator-app package
	@echo "$(BLUE)🧪 Testing document-generator-app...$(NC)"
	$(uv) run --package document-generator-app pytest

.PHONY: test-recipe-executor-app
test-recipe-executor-app: ## Test recipe-executor-app package
	@echo "$(BLUE)🧪 Testing recipe-executor-app...$(NC)"
	$(uv) run --package recipe-executor-app pytest

.PHONY: test-recipe-tool-app
test-recipe-tool-app: ## Test recipe-tool-app package
	@echo "$(BLUE)🧪 Testing recipe-tool-app...$(NC)"
	$(uv) run --package recipe-tool-app pytest

.PHONY: test-python-code-tools
test-python-code-tools: ## Test python-code-tools package
	@echo "$(BLUE)🧪 Testing python-code-tools...$(NC)"
	$(uv) run --package python-code-tools pytest

.PHONY: test-recipe-tool-mcp-server
test-recipe-tool-mcp-server: ## Test recipe-tool-mcp-server package
	@echo "$(BLUE)🧪 Testing recipe-tool-mcp-server...$(NC)"
	$(uv) run --package recipe-tool-mcp-server pytest

# ================================
# Code Quality
# ================================

.PHONY: lint
lint: ## Run linting on all code
	@echo "$(BLUE)🔍 Linting all code...$(NC)"
	$(uv) run ruff check .
	@echo "$(GREEN)✅ Linting completed$(NC)"

.PHONY: lint-fix
lint-fix: ## Run linting and fix auto-fixable issues
	@echo "$(BLUE)🔧 Linting and fixing issues...$(NC)"
	$(uv) run ruff check . --fix
	@echo "$(GREEN)✅ Linting and fixes completed$(NC)"

.PHONY: format
format: ## Format all code
	@echo "$(BLUE)✨ Formatting all code...$(NC)"
	$(uv) run ruff format .
	@echo "$(GREEN)✅ Code formatting completed$(NC)"

.PHONY: typecheck
typecheck: ## Run type checking
	@echo "$(BLUE)🔎 Running type checks...$(NC)"
	$(uv) run pyright
	@echo "$(GREEN)✅ Type checking completed$(NC)"

.PHONY: check
check: lint typecheck test ## Run full check (lint + types + tests)
	@echo "$(GREEN)✅ All checks passed!$(NC)"

# ================================
# Building
# ================================

.PHONY: build
build: ## Build all packages
	@echo "$(BLUE)📦 Building all packages...$(NC)"
	$(uv) build --all
	@echo "$(GREEN)✅ All packages built$(NC)"

# Individual package building
.PHONY: build-recipe-executor
build-recipe-executor: ## Build recipe-executor package
	@echo "$(BLUE)📦 Building recipe-executor...$(NC)"
	$(uv) build --package recipe-executor

.PHONY: build-recipe-tool
build-recipe-tool: ## Build recipe-tool package
	@echo "$(BLUE)📦 Building recipe-tool...$(NC)"
	$(uv) build --package recipe-tool

.PHONY: build-document-generator-app
build-document-generator-app: ## Build document-generator-app package
	@echo "$(BLUE)📦 Building document-generator-app...$(NC)"
	$(uv) build --package document-generator-app

.PHONY: build-recipe-executor-app
build-recipe-executor-app: ## Build recipe-executor-app package
	@echo "$(BLUE)📦 Building recipe-executor-app...$(NC)"
	$(uv) build --package recipe-executor-app

.PHONY: build-recipe-tool-app
build-recipe-tool-app: ## Build recipe-tool-app package
	@echo "$(BLUE)📦 Building recipe-tool-app...$(NC)"
	$(uv) build --package recipe-tool-app

.PHONY: build-python-code-tools
build-python-code-tools: ## Build python-code-tools package
	@echo "$(BLUE)📦 Building python-code-tools...$(NC)"
	$(uv) build --package python-code-tools

.PHONY: build-recipe-tool-mcp-server
build-recipe-tool-mcp-server: ## Build recipe-tool-mcp-server package
	@echo "$(BLUE)📦 Building recipe-tool-mcp-server...$(NC)"
	$(uv) build --package recipe-tool-mcp-server

# ================================
# Publishing
# ================================

.PHONY: publish-test
publish-test: ## Publish all packages to Test PyPI (in dependency order)
	@echo "$(BLUE)🚀 Publishing to Test PyPI...$(NC)"
	@echo "$(YELLOW)Publishing in dependency order...$(NC)"
	$(uv) publish --package python-code-tools --repository testpypi
	@echo "$(YELLOW)⏳ Waiting for PyPI processing...$(NC)" && sleep 10
	$(uv) publish --package recipe-executor --repository testpypi
	@echo "$(YELLOW)⏳ Waiting for PyPI processing...$(NC)" && sleep 10
	$(uv) publish --package recipe-tool --repository testpypi
	@echo "$(YELLOW)⏳ Waiting for PyPI processing...$(NC)" && sleep 10
	$(uv) publish --package document-generator-app --repository testpypi
	$(uv) publish --package recipe-executor-app --repository testpypi
	$(uv) publish --package recipe-tool-app --repository testpypi
	@echo "$(YELLOW)⏳ Waiting for PyPI processing...$(NC)" && sleep 10
	$(uv) publish --package recipe-tool-mcp-server --repository testpypi
	@echo "$(GREEN)✅ All packages published to Test PyPI$(NC)"

.PHONY: publish
publish: ## Publish all packages to PyPI (in dependency order)
	@echo "$(RED)⚠️  Publishing to production PyPI!$(NC)"
	@echo "$(YELLOW)This will publish packages publicly. Continue? [y/N]$(NC)" && read ans && [ $${ans:-N} = y ]
	@echo "$(BLUE)🚀 Publishing to PyPI...$(NC)"
	@echo "$(YELLOW)Publishing in dependency order...$(NC)"
	$(uv) publish --package python-code-tools
	@echo "$(YELLOW)⏳ Waiting for PyPI processing...$(NC)" && sleep 10
	$(uv) publish --package recipe-executor
	@echo "$(YELLOW)⏳ Waiting for PyPI processing...$(NC)" && sleep 10
	$(uv) publish --package recipe-tool
	@echo "$(YELLOW)⏳ Waiting for PyPI processing...$(NC)" && sleep 10
	$(uv) publish --package document-generator-app
	$(uv) publish --package recipe-executor-app
	$(uv) publish --package recipe-tool-app
	@echo "$(YELLOW)⏳ Waiting for PyPI processing...$(NC)" && sleep 10
	$(uv) publish --package recipe-tool-mcp-server
	@echo "$(GREEN)✅ All packages published to PyPI$(NC)"

# ================================
# Running Tools
# ================================

.PHONY: run-recipe-executor
run-recipe-executor: ## Run recipe-executor CLI (usage: make run-recipe-executor ARGS="<args>")
	$(uv) run recipe-executor $(ARGS)

.PHONY: run-recipe-tool
run-recipe-tool: ## Run recipe-tool CLI (usage: make run-recipe-tool ARGS="<args>")
	$(uv) run recipe-tool $(ARGS)

.PHONY: run
run: ## Run arbitrary command (usage: make run CMD="<command>")
	$(uv) run $(CMD)

# ================================
# Development Utilities
# ================================

.PHONY: clean
clean: ## Clean up generated files and caches
	@echo "$(BLUE)🧹 Cleaning workspace...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage
	@echo "$(GREEN)✅ Workspace cleaned$(NC)"

.PHONY: clean-all
clean-all: clean ## Clean everything including virtual environment and lock files
	@echo "$(BLUE)🧹 Deep cleaning workspace...$(NC)"
	rm -rf .venv/
	rm -f uv.lock
	@echo "$(GREEN)✅ Deep clean completed$(NC)"

.PHONY: refresh
refresh: ## Refresh workspace (clean lock + reinstall)
	@echo "$(BLUE)🔄 Refreshing workspace...$(NC)"
	rm -f uv.lock
	$(uv) sync --group dev
	@echo "$(GREEN)✅ Workspace refreshed$(NC)"

.PHONY: doctor
doctor: ## Check workspace health
	@echo "$(BLUE)🏥 Checking workspace health...$(NC)"
	@echo "$(YELLOW)Checking uv installation...$(NC)"
	@$(uv) --version || (echo "$(RED)❌ uv not found$(NC)" && exit 1)
	@echo "$(YELLOW)Checking virtual environment...$(NC)"
	@test -d .venv && echo "$(GREEN)✅ Virtual environment exists$(NC)" || echo "$(RED)❌ Virtual environment missing$(NC)"
	@echo "$(YELLOW)Checking lock file...$(NC)"
	@test -f uv.lock && echo "$(GREEN)✅ Lock file exists$(NC)" || echo "$(RED)❌ Lock file missing$(NC)"
	@echo "$(YELLOW)Checking workspace members...$(NC)"
	@for dir in recipe-executor recipe-tool apps/document-generator apps/recipe-executor apps/recipe-tool mcp-servers/python-code-tools mcp-servers/recipe-tool; do \
		if [ -f "$$dir/pyproject.toml" ]; then \
			echo "$(GREEN)✅ $$dir$(NC)"; \
		else \
			echo "$(RED)❌ $$dir (missing pyproject.toml)$(NC)"; \
		fi \
	done
	@echo "$(GREEN)🏥 Health check completed$(NC)"

# ================================
# Backwards Compatibility
# ================================

.PHONY: recipe-executor-create
recipe-executor-create: ai-context-files ## Legacy: Generate recipe executor code from scratch
	@echo "$(YELLOW)⚠️  Legacy target - consider using individual commands$(NC)"
	@echo "$(BLUE)🔧 Generating recipe executor code...$(NC)"
	$(uv) run recipe-tool --create recipes/recipe_creator/prompts/create_recipe_executor.md

.PHONY: recipe-executor-edit
recipe-executor-edit: ai-context-files ## Legacy: Revise existing recipe executor code
	@echo "$(YELLOW)⚠️  Legacy target - consider using individual commands$(NC)"
	@echo "$(BLUE)🔧 Editing recipe executor code...$(NC)"
	$(uv) run recipe-tool --create recipes/recipe_creator/prompts/edit_recipe_executor.md
