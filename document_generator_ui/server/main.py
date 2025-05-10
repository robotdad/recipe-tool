from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
import json
from fastapi.staticfiles import StaticFiles
from fastapi import UploadFile, File, Form
import uuid
import os
import logging
import logging.handlers
# Delay import of recipe_executor until run_generation to avoid dependency issues
from fastapi.responses import FileResponse

# Determine base directory of this script (document_generator_ui/server)
BASE_DIR = Path(__file__).resolve().parent.parent
# Static SPA directory
STATIC_DIR = BASE_DIR / "static"
# Upload resources into ui/uploads so paths align with the UI project
UPLOAD_DIR = BASE_DIR / "uploads"

app = FastAPI(
    title="Document Generator UI",
    description="Static SPA backend for Document Generator",
)
# Ensure upload directory exists (create parent ai_context/uploads)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
 # Outline file store
OUTLINE_PATH = BASE_DIR / "outline.json"
DEFAULT_OUTLINE = {
    "title": "",
    "general_instruction": "",
    "resources": [],
    "sections": []
}


# Outline load/save endpoints for v1
@app.get("/api/outline")
async def get_outline():
    """Return the current outline JSON (from file or default)."""
    try:
        if OUTLINE_PATH.exists():
            data = OUTLINE_PATH.read_text()
            return json.loads(data)
        else:
            return DEFAULT_OUTLINE
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load outline: {e}")

@app.post("/api/outline")
async def post_outline(outline: dict):
    """Save the provided outline JSON to file."""
    try:
        OUTLINE_PATH.write_text(json.dumps(outline, indent=2))
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save outline: {e}")

@app.get("/api/resources")
async def get_resources():
    """List uploaded resources from the current outline."""
    try:
        if OUTLINE_PATH.exists():
            outline = json.loads(OUTLINE_PATH.read_text())
            return outline.get('resources', [])
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load resources: {e}")

@app.post("/api/resource")
async def upload_resource(
    file: UploadFile = File(...),
    description: str = Form(None)
):
    """Upload a new resource file with optional description."""
    try:
        key = uuid.uuid4().hex
        orig_name = file.filename
        if not orig_name:
            raise HTTPException(status_code=400, detail="Filename is required")
        # Save file using original filename
        dest = UPLOAD_DIR / orig_name
        # Save file
        content = await file.read()
        dest.write_bytes(content)
        # Update metadata in outline.json
        if OUTLINE_PATH.exists():
            outline = json.loads(OUTLINE_PATH.read_text())
        else:
            outline = DEFAULT_OUTLINE.copy()
        # Compute relative path from project root so recipes can load files correctly
        project_root = BASE_DIR.parent
        rel_path = os.path.relpath(dest, project_root)
        # Store key, path, and optional description; UI can derive filename from path
        # Store key, path, and optional description; UI will derive filename from path
        # Store only key, path, and optional description; UI derives filename from path
        entry = {"key": key, "path": rel_path, "description": description or ""}
        outline.setdefault('resources', []).append(entry)
        OUTLINE_PATH.write_text(json.dumps(outline, indent=2))
        return entry
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload resource: {e}")

@app.delete("/api/resource/{key}")
async def delete_resource(key: str):
    """Delete an uploaded resource by key."""
    try:
        # Load outline and resources
        if not OUTLINE_PATH.exists():
            raise HTTPException(status_code=404, detail="No outline/resources found")
        outline = json.loads(OUTLINE_PATH.read_text())
        resources = outline.get('resources', [])
        entry = next((r for r in resources if r.get('key') == key), None)
        if not entry:
            raise HTTPException(status_code=404, detail="Resource not found")
        # Delete file at stored path
        project_root = BASE_DIR.parent
        file_path = project_root / entry.get("path", "")
        if file_path.exists():
            file_path.unlink()
        # Remove resource entry from outline and save
        outline['resources'] = [r for r in resources if r.get('key') != key]
        OUTLINE_PATH.write_text(json.dumps(outline, indent=2))
        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete resource: {e}")

@app.post("/api/run")
async def run_generation(model: Optional[str] = None, output_root: Optional[str] = None):
    """Trigger document generation using the recipe executor."""
    # Ensure working directory is project root so relative recipe paths resolve correctly
    os.chdir(BASE_DIR.parent)
    # Setup logger to capture events
    log_handler = logging.handlers.BufferingHandler(capacity=1000)
    logger = logging.getLogger(f"docgen_ui_{uuid.uuid4().hex}")
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    log_handler.setFormatter(fmt)
    logger.addHandler(log_handler)
    # Read outline path
    if not OUTLINE_PATH.exists():
        raise HTTPException(status_code=400, detail="No outline found. Please save an outline first.")
    # Lazy imports for recipe execution
    from recipe_executor.context import Context
    from recipe_executor.executor import Executor
    # Prepare context artifacts
    artifacts = {"outline_file": str(OUTLINE_PATH)}
    # Recipe config overrides
    cfg = {}
    if model:
        cfg["model"] = model
    if output_root:
        cfg["output_root"] = output_root
    # default recipe_root points to recipes/document_generator
    cfg["recipe_root"] = str(BASE_DIR.parent / "recipes" / "document_generator")
    # Execute recipe
    ctx = Context(artifacts=artifacts, config=cfg)
    executor = Executor(logger)
    recipe_path = str(BASE_DIR.parent / "recipes" / "document_generator" / "build.json")
    try:
        await executor.execute(recipe_path, ctx)
    except Exception as e:
        # Return logs and error
        return {"status": "error", "error": str(e), "logs": [r.getMessage() for r in log_handler.buffer]}
    # Determine output file name
    outline = ctx.get("outline", {})
    # Use fallback when title is empty or missing
    title = outline.get("title") or "document"
    # simple snakecase to uppercase
    fname = title.strip().lower().replace(" ", "_")
    fname = fname.upper() + ".md"
    download_url = f"/api/download/{fname}"
    return {"status": "ok", "logs": [r.getMessage() for r in log_handler.buffer], "download_url": download_url}

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download the generated document file."""
    # Default output directory
    out_dir = BASE_DIR.parent / "output"
    file_path = out_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Generated file not found")
    return FileResponse(path=str(file_path), media_type="text/markdown", filename=filename)

# Mount the SPA static files at the root URL (must be after API routes)
app.mount(
    "/",
    StaticFiles(directory=str(STATIC_DIR), html=True),
    name="static",
)