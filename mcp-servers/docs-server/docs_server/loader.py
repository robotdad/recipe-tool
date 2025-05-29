"""Document loader for the documentation server."""

import fnmatch
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union

import aiofiles
import httpx

from .config import DocsServerSettings


class DocumentLoader:
    """Loads and caches documentation files."""

    def __init__(self, settings: DocsServerSettings):
        self.settings = settings
        self._cache: Dict[str, tuple[str, datetime]] = {}
        self._file_index: Optional[List[Union[Path, str]]] = None
        self._index_time: Optional[datetime] = None

    def _should_include(self, path: Path) -> bool:
        """Check if a file should be included based on patterns."""
        # For URLs, extract just the filename part
        path_str = str(path)
        if path_str.startswith(("http://", "https://")):
            # Get the last part of the URL as the filename
            name = path_str.split("/")[-1]
        else:
            name = path.name

        # Check exclude patterns first
        for pattern in self.settings.exclude_patterns:
            if fnmatch.fnmatch(name, pattern):
                return False

        # Check include patterns
        for pattern in self.settings.include_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True

        return False

    async def _scan_directory(self, path: Path) -> List[Path]:
        """Recursively scan a directory for documentation files."""
        files = []

        try:
            for item in path.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    files.extend(await self._scan_directory(item))
                elif item.is_file() and self._should_include(item):
                    if item.stat().st_size <= self.settings.max_file_size:
                        files.append(item)
        except PermissionError:
            pass  # Skip directories we can't access

        return files

    async def get_file_index(self) -> List[Union[Path, str]]:
        """Get an index of all available documentation files and URLs."""
        # Check if we need to refresh the index
        if (
            self._file_index is None
            or self._index_time is None
            or datetime.now() - self._index_time > timedelta(seconds=60)
        ):
            files = []

            for doc_path in self.settings.doc_paths:
                # Handle URLs (which are kept as strings)
                if isinstance(doc_path, str) and doc_path.startswith(("http://", "https://")):
                    path_str = doc_path
                    # Check if URL matches include patterns (based on filename)
                    url_filename = path_str.split("/")[-1]
                    include = False
                    for pattern in self.settings.include_patterns:
                        if fnmatch.fnmatch(url_filename, pattern):
                            include = True
                            break

                    if include:
                        # Pre-fetch URL content to ensure it's available
                        print(f"Fetching URL: {path_str}")
                        content = await self._load_url(path_str)
                        if content:
                            # Add URL to index as a string
                            files.append(path_str)
                            print(f"Successfully indexed URL: {path_str}")
                        else:
                            # Log failed URL fetch
                            print(f"Warning: Failed to fetch URL: {path_str}")
                else:
                    # Handle Path objects
                    path = doc_path if isinstance(doc_path, Path) else Path(doc_path)
                    path = path.resolve()

                    if path.is_file() and self._should_include(path):
                        files.append(path)
                    elif path.is_dir():
                        files.extend(await self._scan_directory(path))

            # Sort with mixed types (strings and Path objects)
            unique_files = list(set(files))
            self._file_index = sorted(unique_files, key=lambda x: str(x))
            self._index_time = datetime.now()

        return self._file_index

    async def load_file(self, file_path: Union[Path, str]) -> Optional[str]:
        """Load a documentation file or URL with caching."""
        path_str = str(file_path)

        # Check if it's a URL
        if path_str.startswith(("http://", "https://")):
            return await self._load_url(path_str)

        file_path = Path(file_path).resolve()

        # Check cache
        if self.settings.enable_cache and str(file_path) in self._cache:
            content, cached_time = self._cache[str(file_path)]
            if datetime.now() - cached_time < timedelta(seconds=self.settings.cache_ttl):
                return content

        # Load file
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()

            # Update cache
            if self.settings.enable_cache:
                self._cache[str(file_path)] = (content, datetime.now())

            return content
        except Exception:
            return None

    async def search_files(self, query: str) -> List[tuple[Union[Path, str], str]]:
        """Search for files containing the query string."""
        query_lower = query.lower()
        results = []

        files = await self.get_file_index()

        for file_path in files:
            content = await self.load_file(file_path)
            if content and query_lower in content.lower():
                # Extract a snippet around the match
                index = content.lower().find(query_lower)
                start = max(0, index - 100)
                end = min(len(content), index + len(query) + 100)
                snippet = content[start:end]

                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."

                results.append((file_path, snippet))

        return results

    async def _load_url(self, url: str) -> Optional[str]:
        """Load content from a URL."""
        # Check cache first
        if self.settings.enable_cache and url in self._cache:
            content, cached_time = self._cache[url]
            if datetime.now() - cached_time < timedelta(seconds=self.settings.cache_ttl):
                return content

        # Fetch URL
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0, follow_redirects=True)
                response.raise_for_status()
                content = response.text

            # Update cache
            if self.settings.enable_cache:
                self._cache[url] = (content, datetime.now())

            return content
        except Exception as e:
            print(f"Error fetching URL {url}: {type(e).__name__}: {str(e)}")
            return None

    def clear_cache(self):
        """Clear the document cache."""
        self._cache.clear()
        self._file_index = None
        self._index_time = None
