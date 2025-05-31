# AI Context System - Implementation Guide

## Overview

This is a comprehensive guide for implementing an AI context generation system that collects codebase files into organized Markdown documents for AI development tools. The system was originally developed in the recipe-tool project and can be adapted for any large codebase.

## What This System Does

The AI context system automatically scans your codebase and generates consolidated Markdown files containing:
- Source code from specific directories/patterns
- Configuration files and documentation
- External library documentation (optional)
- Metadata about file counts, timestamps, and search patterns

This provides AI tools with comprehensive context about your project without needing to scan the entire repository each time.

## Core Components

### 1. `tools/collect_files.py`
**Purpose**: Core utility for pattern-based file collection
**Key Features**:
- Recursive directory scanning with glob patterns
- Flexible include/exclude pattern matching
- Binary file detection and handling
- UTF-8 encoding with fallback handling
- Generates formatted Markdown output with file separators

**Default Exclusions**: `.venv`, `node_modules`, `*.lock`, `.git`, `__pycache__`, `*.pyc`, `*.ruff_cache`, `logs`, `output`

### 2. `tools/build_ai_context_files.py`
**Purpose**: Main orchestrator that defines what gets collected
**Key Features**:
- Defines collection "tasks" - each creates one output file
- Smart file comparison (only overwrites if content changed, ignoring timestamps)
- Configurable output directory (`ai_context/generated` by default)
- Force flag to always overwrite files

**Task Structure**:
```python
{
    "patterns": ["directory/to/scan"],           # What to scan
    "output": f"{OUTPUT_DIR}/OUTPUT_FILE.md",    # Where to save
    "exclude": collect_files.DEFAULT_EXCLUDE,    # What to skip
    "include": ["specific_files.json"],          # Force include these
}
```

### 3. `tools/build_git_collector_files.py`
**Purpose**: Downloads external documentation using git-collector tool
**Key Features**:
- Multiple fallback strategies (global install, pnpm, npx)
- Automatically installs git-collector via npx if needed
- Outputs to `ai_context/git_collector` directory
- Graceful failure with installation guidance

## Implementation Steps

### Step 1: Copy Core Files
Copy these files from the recipe-tool project:
- `tools/collect_files.py` (no changes needed)
- `tools/build_ai_context_files.py` (needs customization)
- `tools/build_git_collector_files.py` (optional, may need customization)

### Step 2: Customize for Your Project
Edit `build_ai_context_files.py` and modify the `tasks` list in the `build_context_files()` function to match your project structure.

**Example customizations**:

For a large web application:
```python
tasks = [
    # Frontend code
    {
        "patterns": ["frontend/src"],
        "output": f"{OUTPUT_DIR}/FRONTEND_SOURCE.md",
        "exclude": collect_files.DEFAULT_EXCLUDE,
        "include": ["package.json", "tsconfig.json"],
    },
    # Backend API
    {
        "patterns": ["backend/api"],
        "output": f"{OUTPUT_DIR}/BACKEND_API.md",
        "exclude": collect_files.DEFAULT_EXCLUDE,
        "include": ["requirements.txt", "pyproject.toml"],
    },
    # Database schemas
    {
        "patterns": ["database/migrations", "database/schemas"],
        "output": f"{OUTPUT_DIR}/DATABASE_SCHEMA.md",
        "exclude": collect_files.DEFAULT_EXCLUDE,
        "include": [],
    },
    # Configuration
    {
        "patterns": ["config", "*.yaml", "*.json", "docker-compose.yml"],
        "output": f"{OUTPUT_DIR}/CONFIGURATION.md",
        "exclude": collect_files.DEFAULT_EXCLUDE + ["node_modules"],
        "include": [],
    },
    # Tests
    {
        "patterns": ["tests", "**/*test.py", "**/*.spec.js"],
        "output": f"{OUTPUT_DIR}/TESTS.md",
        "exclude": collect_files.DEFAULT_EXCLUDE,
        "include": [],
    },
    # Documentation
    {
        "patterns": ["docs", "*.md"],
        "output": f"{OUTPUT_DIR}/DOCUMENTATION.md",
        "exclude": collect_files.DEFAULT_EXCLUDE,
        "include": [],
    },
]
```

### Step 3: Add Build Integration
Add to your `Makefile`:
```makefile
.PHONY: ai-context-files
ai-context-files: ## Build AI context files for development
	@echo "Building AI context files..."
	python tools/build_ai_context_files.py
	python tools/build_git_collector_files.py  # Optional
	@echo "AI context files generated in ai_context/generated/"
```

Or create a shell script:
```bash
#!/bin/bash
echo "Building AI context files..."
python tools/build_ai_context_files.py
echo "AI context files generated in ai_context/generated/"
```

## Usage

### Basic Usage
```bash
make ai-context-files
# Or directly:
python tools/build_ai_context_files.py
```

### Force Regeneration
```bash
python tools/build_ai_context_files.py --force
```

### Manual File Collection
```bash
# Collect specific patterns
python tools/collect_files.py "src/**/*.py" "config/*.yaml" > my_context.md

# With exclusions
python tools/collect_files.py "src" --exclude "tests,__pycache__" > source_only.md

# With forced inclusions
python tools/collect_files.py "src" --exclude "config" --include "config/important.yaml" > source_with_config.md
```

## Output Structure

Generated files appear in:
- `ai_context/generated/` - Your codebase files
- `ai_context/git_collector/` - External documentation (if using git-collector)

Each file contains:
- Header with search patterns, exclusions, timestamp, file count
- Individual files separated by `=== File: path/to/file.py ===`
- Complete file contents (binary files show `[Binary file not displayed]`)

## Performance Considerations for Large Projects

### 1. Split by Logical Components
Don't create one massive file. Split into logical components:
```python
# Good: Split by component
{"patterns": ["frontend/components"], "output": "FRONTEND_COMPONENTS.md"}
{"patterns": ["backend/services"], "output": "BACKEND_SERVICES.md"}

# Bad: Everything in one file
{"patterns": ["frontend", "backend"], "output": "EVERYTHING.md"}
```

### 2. Use Strategic Exclusions
Add project-specific exclusions:
```python
exclude = collect_files.DEFAULT_EXCLUDE + [
    "generated",     # Generated code
    "vendor",        # Third-party code
    "assets/images", # Binary assets
    "*.min.js",      # Minified files
    "coverage",      # Test coverage reports
]
```

### 3. Consider File Size Limits
For very large projects, you may want to add file size limits or line count limits to the `collect_files.py` script.

## Troubleshooting

### Git-Collector Issues
If `build_git_collector_files.py` fails:
1. Install globally: `npm i -g git-collector`
2. Or disable it by not running that script
3. Or remove external docs collection entirely

### Permission Issues
Ensure the script has write permissions to create `ai_context/` directory.

### Memory Issues on Large Projects
If you run into memory issues:
1. Split tasks into smaller chunks
2. Add more specific exclude patterns
3. Consider processing subdirectories separately

## Customization Tips

### For Monorepos
Create separate tasks for each service/package:
```python
services = ["auth", "payment", "notification", "analytics"]
for service in services:
    tasks.append({
        "patterns": [f"services/{service}"],
        "output": f"{OUTPUT_DIR}/{service.upper()}_SERVICE.md",
        "exclude": collect_files.DEFAULT_EXCLUDE,
        "include": [],
    })
```

### For Multi-Language Projects
Separate by language:
```python
# Python backend
{"patterns": ["**/*.py"], "output": "PYTHON_CODE.md"}
# JavaScript frontend  
{"patterns": ["**/*.js", "**/*.ts"], "output": "JAVASCRIPT_CODE.md"}
# Go microservices
{"patterns": ["**/*.go"], "output": "GO_CODE.md"}
```

### For Documentation-Heavy Projects
```python
# API documentation
{"patterns": ["docs/api"], "output": "API_DOCS.md"}
# User guides
{"patterns": ["docs/user"], "output": "USER_DOCS.md"}
# Architecture docs
{"patterns": ["docs/architecture"], "output": "ARCHITECTURE_DOCS.md"}
```

## Integration with AI Tools

The generated files are designed to be:
1. **Easily consumable** by AI tools via simple file reading
2. **Well-structured** with clear file boundaries and metadata
3. **Comprehensive** without being overwhelming
4. **Up-to-date** through automated regeneration

Use these files to provide context to:
- Code review tools
- Documentation generators
- Automated testing tools
- Architecture analysis tools
- Any AI assistant working on your codebase

## Best Practices

1. **Run regularly** - Add to CI/CD or git hooks to keep context fresh
2. **Version control** - Commit the generated files so team members have consistent context
3. **Document your patterns** - Add comments explaining why you chose specific patterns
4. **Monitor file sizes** - Large files may hit AI token limits
5. **Regular cleanup** - Remove obsolete context files when refactoring

---

**Date Created**: 2025-01-28
**Source Project**: recipe-tool (https://github.com/microsoft/recipe-tool)
**Implementation**: Copy the three Python files and customize the tasks list in `build_ai_context_files.py`