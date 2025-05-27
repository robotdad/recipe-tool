"""Tests for the utility functions."""

import json
import os
import tempfile
from unittest.mock import patch

import pytest

from recipe_executor_app.utils import (
    create_temp_file,
    format_results,
    get_repo_root,
    parse_context_vars,
    read_file,
    safe_json_dumps,
)


class TestParseContextVars:
    """Tests for parse_context_vars function."""

    def test_empty_string(self):
        """Test with an empty string."""
        result = parse_context_vars("")
        assert result == {}

    def test_none_value(self):
        """Test with None value."""
        result = parse_context_vars(None)
        assert result == {}

    def test_single_pair(self):
        """Test with a single key-value pair."""
        result = parse_context_vars("key=value")
        assert result == {"key": "value"}

    def test_multiple_pairs(self):
        """Test with multiple key-value pairs."""
        result = parse_context_vars("key1=value1,key2=value2")
        assert result == {"key1": "value1", "key2": "value2"}

    def test_no_equals_sign(self):
        """Test with no equals sign in the value."""
        result = parse_context_vars("key1=value1,key2")
        assert result == {"key1": "value1"}  # key2 without value is ignored


class TestCreateTempFile:
    """Tests for create_temp_file function."""

    def test_create_temp_file(self):
        """Test creating a temporary file."""
        content = "Test content"
        path, cleanup = create_temp_file(content)

        # Verify file exists and has content
        assert os.path.exists(path)
        with open(path, "r") as f:
            assert f.read() == content

        # Clean up
        cleanup()
        assert not os.path.exists(path)

    def test_create_temp_file_with_suffix(self):
        """Test creating a temporary file with custom suffix."""
        content = "Test content"
        path, cleanup = create_temp_file(content, suffix=".json")

        # Verify file has correct suffix
        assert path.endswith(".json")

        # Clean up
        cleanup()


class TestFormatResults:
    """Tests for format_results function."""

    def test_empty_results(self):
        """Test with empty results."""
        result = format_results({})
        assert "Recipe Execution Results" in result
        assert "Execution Time" in result

    def test_with_results(self):
        """Test with results."""
        results = {"output": "Test output", "result_text": "Test result"}
        result = format_results(results)
        assert "Recipe Execution Results" in result
        assert "output" in result
        assert "Test output" in result
        assert "result_text" in result
        assert "Test result" in result

    def test_with_execution_time(self):
        """Test with execution time."""
        result = format_results({}, execution_time=1.23)
        assert "Execution Time**: 1.23s" in result

    def test_with_json_content(self):
        """Test with JSON-like content."""
        results = {"output": '{"key": "value"}'}
        result = format_results(results)
        assert "```json" in result
        assert '{"key": "value"}' in result


class TestSafeJsonDumps:
    """Tests for safe_json_dumps function."""

    def test_simple_dict(self):
        """Test with a simple dictionary."""
        data = {"key1": "value1", "key2": "value2"}
        result = safe_json_dumps(data)
        assert json.loads(result) == data

    def test_non_serializable(self):
        """Test with non-serializable object."""

        class NonSerializable:
            def __str__(self):
                return "NonSerializable"

        data = {"key": NonSerializable()}
        result = safe_json_dumps(data)
        parsed = json.loads(result)
        assert parsed["key"] == "NonSerializable"

    def test_exception_handling(self):
        """Test exception handling in safe_json_dumps."""
        # Create an object that will cause an exception even with default=str
        import math

        data = {"nan": math.nan}
        result = safe_json_dumps(data)
        # Should still return valid JSON
        assert json.loads(result) is not None


class TestReadFile:
    """Tests for read_file function."""

    def test_read_existing_file(self):
        """Test reading an existing file."""
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            f.write("Test content")
            f.flush()
            path = f.name

        try:
            result = read_file(path)
            assert result == "Test content"
        finally:
            os.unlink(path)

    def test_read_nonexistent_file(self):
        """Test reading a nonexistent file."""
        with pytest.raises(FileNotFoundError):
            read_file("/nonexistent/file.txt")


class TestGetRepoRoot:
    """Tests for get_repo_root function."""

    @patch("os.path.exists")
    @patch("os.path.dirname")
    @patch("os.path.abspath")
    def test_get_repo_root(self, mock_abspath, mock_dirname, mock_exists):
        """Test get_repo_root function."""
        # Setup
        mock_abspath.return_value = "/path/to/repo/subdir/file.py"
        mock_dirname.side_effect = [
            "/path/to/repo/subdir",
            "/path/to/repo",
        ]
        mock_exists.side_effect = [False, True]  # pyproject.toml found in second dir

        # Execute
        result = get_repo_root()

        # Verify
        assert result == "/path/to/repo"
