"""MCP server implementation for documentation."""

from pathlib import Path
from typing import List, Union

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
            List of file paths as configured (e.g., '../../ai_context/generated/file.md').
        """
        files = await loader.get_file_index()

        result = []
        for file_path in files:
            # URLs are stored as strings, return as-is
            if isinstance(file_path, str):
                result.append(file_path)
            else:
                # For files, find which doc_path it belongs to and show relative to that
                found = False
                for doc_path in settings.doc_paths:
                    if isinstance(doc_path, str) and doc_path.startswith(('http://', 'https://')):
                        continue
                    
                    doc_path_obj = doc_path if isinstance(doc_path, Path) else Path(doc_path)
                    try:
                        # Check if this file is under this doc_path
                        rel_path = file_path.relative_to(doc_path_obj.resolve())
                        # Return it as configured doc_path + relative path
                        result.append(str(doc_path / rel_path))
                        found = True
                        break
                    except ValueError:
                        continue
                
                if not found:
                    # If file is the doc_path itself, return as configured
                    for doc_path in settings.doc_paths:
                        if isinstance(doc_path, str) and doc_path.startswith(('http://', 'https://')):
                            continue
                        doc_path_obj = doc_path if isinstance(doc_path, Path) else Path(doc_path)
                        if doc_path_obj.resolve() == file_path:
                            result.append(str(doc_path))
                            found = True
                            break
                    
                    if not found:
                        # Fallback to absolute path
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
        # Check if it's a URL first
        if file_path.startswith(('http://', 'https://')):
            # Validate URL is in our index
            files = await loader.get_file_index()
            if file_path not in [f for f in files if isinstance(f, str)]:
                return f"Error: URL '{file_path}' not found in documentation index"
            content = await loader.load_file(file_path)
        else:
            # For file paths, resolve based on our doc_paths
            resolved_path = None
            
            # First check if it matches any doc_path exactly
            for doc_path in settings.doc_paths:
                if isinstance(doc_path, str) and doc_path.startswith(('http://', 'https://')):
                    continue
                if str(doc_path) == file_path:
                    resolved_path = Path(doc_path).resolve()
                    break
            
            # Then check if it's a path under a doc_path
            if not resolved_path:
                path_obj = Path(file_path)
                if path_obj.is_absolute():
                    # Absolute path - validate it's in our index
                    files = await loader.get_file_index()
                    for f in files:
                        if isinstance(f, Path) and f == path_obj:
                            resolved_path = f
                            break
                else:
                    # Relative path - could be relative to current dir or a doc_path
                    # First try as-is
                    candidate = path_obj.resolve()
                    if candidate.exists():
                        files = await loader.get_file_index()
                        for f in files:
                            if isinstance(f, Path) and f == candidate:
                                resolved_path = candidate
                                break
                    
                    # If not found, try relative to each doc_path
                    if not resolved_path:
                        for doc_path in settings.doc_paths:
                            if isinstance(doc_path, str) and doc_path.startswith(('http://', 'https://')):
                                continue
                            doc_path_obj = doc_path if isinstance(doc_path, Path) else Path(doc_path)
                            # For paths like ../../ai_context/generated/file.md
                            # We need to resolve the doc_path first, then append the rest
                            if str(file_path).startswith(str(doc_path)):
                                # Extract the relative part after the doc_path
                                rel_part = str(file_path)[len(str(doc_path)):].lstrip('/')
                                if rel_part:
                                    candidate = doc_path_obj.resolve() / rel_part
                                else:
                                    candidate = doc_path_obj.resolve()
                                
                                if candidate.exists():
                                    files = await loader.get_file_index()
                                    for f in files:
                                        if isinstance(f, Path) and f == candidate:
                                            resolved_path = candidate
                                            break
                                if resolved_path:
                                    break
            
            if not resolved_path:
                return f"Error: File '{file_path}' not found in documentation index"
            
            content = await loader.load_file(resolved_path)
        
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
            if isinstance(file_path, str):
                # URL - return as-is
                formatted_results.append({
                    "file": file_path,
                    "snippet": snippet.strip()
                })
            else:
                # File - find its doc_path and show relative to that
                display_path = str(file_path)  # fallback
                for doc_path in settings.doc_paths:
                    if isinstance(doc_path, str) and doc_path.startswith(('http://', 'https://')):
                        continue
                    
                    doc_path_obj = doc_path if isinstance(doc_path, Path) else Path(doc_path)
                    try:
                        # Check if this file is under this doc_path
                        rel_path = file_path.relative_to(doc_path_obj.resolve())
                        # Return it as configured doc_path + relative path
                        display_path = str(doc_path / rel_path)
                        break
                    except ValueError:
                        # Check if it IS the doc_path
                        if doc_path_obj.resolve() == file_path:
                            display_path = str(doc_path)
                            break
                
                formatted_results.append({
                    "file": display_path,
                    "snippet": snippet.strip()
                })

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
            # Handle both URLs (strings) and Path objects
            if isinstance(file_path, str):
                # For URLs, extract extension from the URL
                if file_path.startswith(('http://', 'https://')):
                    # Get the last part of the URL and extract extension
                    filename = file_path.split('/')[-1]
                    if '.' in filename:
                        ext = '.' + filename.split('.')[-1].lower()
                    else:
                        ext = '.no-extension'
                    extensions[ext] = extensions.get(ext, 0) + 1
                    # Can't get size for URLs without fetching them
            else:
                # For Path objects
                ext = file_path.suffix.lower() if file_path.suffix else '.no-extension'
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
