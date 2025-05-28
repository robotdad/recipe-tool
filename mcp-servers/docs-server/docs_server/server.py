"""MCP server implementation for documentation."""

from pathlib import Path
from typing import List

from mcp.server.fastmcp import FastMCP

from .config import DocsServerSettings
from .loader import DocumentLoader


def create_docs_server(settings: DocsServerSettings) -> FastMCP:
    """Create the MCP server with documentation tools."""
    mcp = FastMCP("Documentation Server")
    loader = DocumentLoader(settings)

    @mcp.tool()
    async def list_docs() -> List[str]:
        """
        List all available documentation files.

        Returns:
            List of file paths relative to the configured documentation roots.
        """
        files = await loader.get_file_index()

        # Convert to relative paths for cleaner display
        result = []
        for file_path in files:
            path_str = str(file_path)
            
            # URLs should be displayed as-is
            if path_str.startswith(('http://', 'https://')):
                result.append(path_str)
            else:
                # Check if this file IS one of the doc_paths
                found = False
                for doc_path in settings.doc_paths:
                    doc_path_str = str(doc_path)
                    if not doc_path_str.startswith(('http://', 'https://')):
                        doc_path_resolved = Path(doc_path).resolve()
                        if doc_path_resolved == file_path:
                            # This file IS a doc_path - show parent/filename
                            if file_path.parent != Path("/"):
                                result.append(f"{file_path.parent.name}/{file_path.name}")
                            else:
                                result.append(file_path.name)
                            found = True
                            break
                
                if not found:
                    # Try to make path relative to one of the doc roots
                    for doc_path in settings.doc_paths:
                        doc_path_str = str(doc_path)
                        # Skip URL doc_paths when making relative paths
                        if doc_path_str.startswith(('http://', 'https://')):
                            continue
                        try:
                            rel_path = file_path.relative_to(Path(doc_path).resolve())
                            rel_path_str = str(rel_path)
                            result.append(rel_path_str)
                            found = True
                            break
                        except ValueError:
                            pass
                    
                    if not found:
                        # If not relative to any doc root, use absolute path
                        result.append(str(file_path))

        return result

    @mcp.tool()
    async def read_doc(file_path: str) -> str:
        """
        Read the contents of a documentation file.

        Args:
            file_path: Path to the documentation file (can be relative or absolute).

        Returns:
            The contents of the file, or an error message if the file cannot be read.
        """
        # Try to resolve the path
        path = Path(file_path)

        if not path.is_absolute():
            # Try to find the file relative to doc roots
            for doc_path in settings.doc_paths:
                candidate = Path(doc_path) / file_path
                if candidate.exists():
                    path = candidate
                    break

        content = await loader.load_file(path)

        if content is None:
            return f"Error: Could not read file '{file_path}'"

        return content

    @mcp.tool()
    async def search_docs(query: str, max_results: int = 10) -> List[dict]:
        """
        Search for documentation files containing the specified query.

        Args:
            query: The search query string.
            max_results: Maximum number of results to return (default: 10).

        Returns:
            List of search results with file paths and matching snippets.
        """
        results = await loader.search_files(query)

        # Limit results
        results = results[:max_results]

        # Format results
        formatted_results = []
        for file_path, snippet in results:
            # Try to make path relative
            display_path = str(file_path)
            
            # URLs should be displayed as-is
            if not display_path.startswith(('http://', 'https://')):
                # Check if this file IS one of the doc_paths
                found = False
                for doc_path in settings.doc_paths:
                    doc_path_str = str(doc_path)
                    if not doc_path_str.startswith(('http://', 'https://')):
                        doc_path_resolved = Path(doc_path).resolve()
                        if doc_path_resolved == file_path:
                            # This file IS a doc_path - show parent/filename
                            if file_path.parent != Path("/"):
                                display_path = f"{file_path.parent.name}/{file_path.name}"
                            else:
                                display_path = file_path.name
                            found = True
                            break
                
                if not found:
                    # Try to make path relative to one of the doc roots
                    for doc_path in settings.doc_paths:
                        doc_path_str = str(doc_path)
                        # Skip URL doc_paths when making relative paths
                        if doc_path_str.startswith(('http://', 'https://')):
                            continue
                        try:
                            rel_path = file_path.relative_to(Path(doc_path).resolve())
                            display_path = str(rel_path)
                            break
                        except ValueError:
                            pass

            formatted_results.append({"file": display_path, "snippet": snippet.strip()})

        return formatted_results

    @mcp.tool()
    async def get_doc_stats() -> dict:
        """
        Get statistics about the documentation.

        Returns:
            Dictionary containing documentation statistics.
        """
        files = await loader.get_file_index()

        # Count files by extension
        extensions = {}
        total_size = 0

        for file_path in files:
            ext = file_path.suffix.lower()
            extensions[ext] = extensions.get(ext, 0) + 1

            try:
                total_size += file_path.stat().st_size
            except OSError:
                pass

        return {
            "total_files": len(files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": extensions,
            "doc_paths": [str(p) for p in settings.doc_paths],
            "cache_enabled": settings.enable_cache,
        }

    @mcp.tool()
    async def clear_cache() -> str:
        """
        Clear the documentation cache and force a refresh.

        Returns:
            Confirmation message.
        """
        loader.clear_cache()
        return "Documentation cache cleared successfully."

    return mcp
