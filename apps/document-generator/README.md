# 📄 Document Generator App

A Gradio web interface for creating structured documents using AI-powered generation. Define document outlines with resources and sections, then generate complete documents using the recipe executor.

## Features

- **Visual Outline Editor**: Create document structures with nested sections (up to 4 levels)
- **Resource Management**: Upload files or reference URLs as source materials
- **Two Generation Modes**:
  - **Prompt Mode**: AI generates content based on prompts and resource references
  - **Static Mode**: Directly include content from resources
- **Live JSON Preview**: See your outline structure in real-time with validation
- **Auto-save**: All changes save automatically as you type
- **Import/Export**: Upload existing outlines or download your work

## Quick Start

### Development Mode
```bash
# From workspace root
make install               # Install dependencies
document-generator-app     # Launch the web interface
```

### Deployment Mode
```bash
# Build self-contained deployment package
make build                 # Bundle recipes + refresh examples

# Then deploy the entire app directory
# The app will automatically use bundled recipes
```

The app will open at `http://localhost:8000`

## How to Use

1. **Add Resources**: Click "+ Add" under Resources to add source files or URLs
   - Set a unique key for each resource
   - Upload files or provide paths/URLs
   - Add descriptions to help the AI understand the content

2. **Create Sections**: Click "+ Add" under Sections to build your document structure
   - Use "+ Sub" to create nested subsections
   - Choose between Prompt mode (AI generation) or Static mode (direct inclusion)
   - Reference resources in your prompts using their keys

3. **Generate Document**: Once your outline validates (green Generate button), click to create your document
   - The AI will process each section according to your instructions
   - Download the generated Markdown file when complete

## Example Outline

```json
{
  "title": "Project README",
  "general_instruction": "Create a comprehensive README for the project",
  "resources": [
    {
      "key": "code_files",
      "path": "./src",
      "description": "Source code files"
    }
  ],
  "sections": [
    {
      "title": "Overview",
      "prompt": "Write a brief project overview based on the code structure",
      "refs": ["code_files"]
    }
  ]
}
```

## Building for Deployment

The app can be built into a self-contained deployment package that includes all recipe files and refreshed examples.

### Build Command

```bash
# From the document-generator directory
make build

# Or run the script directly:
python scripts/build_deployment.py
```

### What the Build Process Does

1. **Bundles Recipe Files**: Copies all recipe files from `/recipes/document_generator/` into `document_generator_app/recipes/`
2. **Refreshes Examples**: Updates example docpacks with latest content and bundled resources  
3. **Updates .gitignore**: Adds bundled recipes to ignore list (since they're generated)
4. **Verifies Build**: Ensures all required files are present and correctly bundled

### Deployment vs Development

- **Development Mode**: App uses recipes from the main repository (`/recipes/document_generator/`)
- **Deployment Mode**: App uses bundled recipes (`document_generator_app/recipes/`)
- **Automatic Detection**: The app automatically detects which mode to use based on file presence

After building, the entire `apps/document-generator/` directory becomes self-contained and can be deployed independently without the rest of the repository.

## Refreshing Example Docpacks (Development)

For development work, you can refresh just the examples without doing a full build:

```bash
# From the document-generator directory
make refresh-examples

# Or run the script directly:
python scripts/refresh_examples.py
```

### Example Sources

- **Source files**: `/recipes/document_generator/examples/*.json`
- **Resource files**: `/recipes/document_generator/examples/resources/`  
- **Generated docpacks**: `apps/document-generator/examples/*.docpack`

The source JSON files contain full file paths to actual resource files. When converted to docpacks, the referenced files are bundled inside the .docpack archive, creating fully functional examples.

## Architecture

The app follows a simple two-column layout:
- **Left Column**: Resource and section management with live JSON preview
- **Right Column**: Editor for the selected item
- **Bottom**: Document generation and output display

Built with Gradio for the UI and uses the recipe-executor for document generation.
