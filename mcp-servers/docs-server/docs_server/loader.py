"""Document loader for the documentation server."""

import fnmatch
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles

from .config import DocsServerSettings


class DocumentLoader:
    """Loads and caches documentation files."""

    def __init__(self, settings: DocsServerSettings):
        self.settings = settings
        self._cache: Dict[str, tuple[str, datetime]] = {}
        self._file_index: Optional[List[Path]] = None
        self._index_time: Optional[datetime] = None

    def _should_include(self, path: Path) -> bool:
        """Check if a file should be included based on patterns."""
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

    async def get_file_index(self) -> List[Path]:
        """Get an index of all available documentation files."""
        # Check if we need to refresh the index
        if (
            self._file_index is None
            or self._index_time is None
            or datetime.now() - self._index_time > timedelta(seconds=60)
        ):
            files = []

            for doc_path in self.settings.doc_paths:
                path = Path(doc_path).resolve()

                if path.is_file() and self._should_include(path):
                    files.append(path)
                elif path.is_dir():
                    files.extend(await self._scan_directory(path))

            self._file_index = sorted(set(files))
            self._index_time = datetime.now()

        return self._file_index

    async def load_file(self, file_path: Path) -> Optional[str]:
        """Load a documentation file with caching."""
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

    async def search_files(self, query: str) -> List[tuple[Path, str]]:
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

    def clear_cache(self):
        """Clear the document cache."""
        self._cache.clear()
        self._file_index = None
        self._index_time = None
