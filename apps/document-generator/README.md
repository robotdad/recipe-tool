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

```bash
# From workspace root
make install               # Install dependencies
document-generator-app     # Launch the web interface
```

The app will open at `http://localhost:7860`

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

## Architecture

The app follows a simple two-column layout:
- **Left Column**: Resource and section management with live JSON preview
- **Right Column**: Editor for the selected item
- **Bottom**: Document generation and output display

Built with Gradio for the UI and uses the recipe-executor for document generation.
