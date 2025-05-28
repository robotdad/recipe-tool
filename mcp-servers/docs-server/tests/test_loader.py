"""Tests for the document loader."""

import tempfile
from pathlib import Path

import pytest

from docs_server.config import DocsServerSettings
from docs_server.loader import DocumentLoader


@pytest.fixture
def temp_docs_dir():
    """Create a temporary directory with test documents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test files
        (tmpdir_path / "readme.md").write_text("# Test Project\n\nThis is a test.")
        (tmpdir_path / "guide.txt").write_text("User Guide\n\nStep 1: Install\nStep 2: Use")
        (tmpdir_path / "hidden.txt").write_text("Hidden file")
        (tmpdir_path / ".hidden").write_text("Should be excluded")

        # Create subdirectory
        subdir = tmpdir_path / "docs"
        subdir.mkdir()
        (subdir / "api.md").write_text("# API Reference\n\n## Functions")

        yield tmpdir_path


@pytest.fixture
def loader(temp_docs_dir):
    """Create a document loader with test settings."""
    settings = DocsServerSettings(
        doc_paths=[temp_docs_dir],
        include_patterns=["*.md", "*.txt"],
        exclude_patterns=[".*", "hidden*"],
    )
    return DocumentLoader(settings)


@pytest.mark.asyncio
async def test_get_file_index(loader, temp_docs_dir):
    """Test getting the file index."""
    files = await loader.get_file_index()

    # Convert to relative paths for easier testing
    rel_files = [f.relative_to(temp_docs_dir) for f in files]
    rel_names = [str(f) for f in rel_files]

    assert "readme.md" in rel_names
    assert "guide.txt" in rel_names
    assert "docs/api.md" in rel_names
    assert ".hidden" not in rel_names
    assert "hidden.txt" not in rel_names


@pytest.mark.asyncio
async def test_load_file(loader, temp_docs_dir):
    """Test loading a file."""
    file_path = temp_docs_dir / "readme.md"
    content = await loader.load_file(file_path)

    assert content is not None
    assert "# Test Project" in content
    assert "This is a test." in content


@pytest.mark.asyncio
async def test_load_file_not_found(loader, temp_docs_dir):
    """Test loading a non-existent file."""
    file_path = temp_docs_dir / "nonexistent.md"
    content = await loader.load_file(file_path)

    assert content is None


@pytest.mark.asyncio
async def test_search_files(loader, temp_docs_dir):
    """Test searching for content in files."""
    results = await loader.search_files("test")

    assert len(results) == 1
    file_path, snippet = results[0]
    assert file_path.name == "readme.md"
    assert "test" in snippet.lower()


@pytest.mark.asyncio
async def test_search_multiple_matches(loader, temp_docs_dir):
    """Test searching with multiple matches."""
    results = await loader.search_files("Guide")

    assert len(results) == 1
    file_path, snippet = results[0]
    assert file_path.name == "guide.txt"
    assert "Guide" in snippet


@pytest.mark.asyncio
async def test_cache_functionality(loader, temp_docs_dir):
    """Test that caching works correctly."""
    file_path = temp_docs_dir / "readme.md"

    # First load
    content1 = await loader.load_file(file_path)

    # Modify the file
    file_path.write_text("Modified content")

    # Second load should return cached content
    content2 = await loader.load_file(file_path)
    assert content1 == content2

    # Clear cache and reload
    loader.clear_cache()
    content3 = await loader.load_file(file_path)
    assert content3 == "Modified content"
