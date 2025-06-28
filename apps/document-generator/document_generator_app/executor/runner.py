"""
Headless generation runner: invoke the document-generator recipe.
"""

import json
from pathlib import Path

from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger

from ..models.outline import Outline
from ..session import session_manager
from ..resource_resolver import resolve_all_resources
from typing import Optional


async def generate_document(outline: Optional[Outline], session_id: Optional[str] = None) -> str:
    """
    Run the document-generator recipe with the given outline and return the generated Markdown.
    """
    # Allow stub invocation without an outline for initial tests
    if outline is None:
        return ""

    # First try bundled recipes (for deployment), then fall back to repo structure (for development)
    APP_ROOT = Path(__file__).resolve().parents[2]  # document_generator_app parent
    BUNDLED_RECIPE_PATH = APP_ROOT / "document_generator_app" / "recipes" / "document_generator_recipe.json"

    if BUNDLED_RECIPE_PATH.exists():
        # Use bundled recipes (deployment mode)
        RECIPE_PATH = BUNDLED_RECIPE_PATH
        RECIPE_ROOT = RECIPE_PATH.parent
    else:
        # Fall back to repo structure (development mode)
        REPO_ROOT = Path(__file__).resolve().parents[4]
        RECIPE_PATH = REPO_ROOT / "recipes" / "document_generator" / "document_generator_recipe.json"
        RECIPE_ROOT = RECIPE_PATH.parent

    # Use session-scoped temp directory
    session_dir = session_manager.get_session_dir(session_id)
    tmpdir = str(session_dir / "execution")
    Path(tmpdir).mkdir(exist_ok=True)

    try:
        # Resolve all resources using the new resolver
        outline_data = outline.to_dict()
        resolved_resources = resolve_all_resources(outline_data, session_id)

        # Update resource paths in outline with resolved paths
        for resource in outline.resources:
            if resource.key in resolved_resources:
                resource.path = str(resolved_resources[resource.key])

        # Create updated outline with resolved paths
        data = outline.to_dict()
        outline_json = json.dumps(data, indent=2)
        outline_path = Path(tmpdir) / "outline.json"
        outline_path.write_text(outline_json)

        logger = init_logger(log_dir=tmpdir)
        context = Context(
            artifacts={
                "outline_file": str(outline_path),
                "recipe_root": str(RECIPE_ROOT),
                "output_root": str(session_dir),  # Use session directory for output
            }
        )
        executor = Executor(logger)
        await executor.execute(str(RECIPE_PATH), context)

        output_root = Path(context.get("output_root", tmpdir))
        filename = context.get("document_filename")
        if not filename:
            return context.get("document", "")

        document_path = output_root / f"{filename}.md"
        try:
            return document_path.read_text()
        except FileNotFoundError:
            return f"Generated file not found: {document_path}"
    except Exception as e:
        return f"Error generating document: {str(e)}"
