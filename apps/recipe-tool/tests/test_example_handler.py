"""Tests for the example_handler module of the recipe_tool_app package."""

from unittest.mock import mock_open, patch

import pytest


@pytest.fixture
def mock_file_content():
    """Sample recipe file content for testing."""
    return """
    {
        "name": "Test Recipe",
        "description": "A test recipe",
        "steps": [
            {"type": "read_files", "config": {"description": "Read file"}}
        ]
    }
    """


@pytest.fixture
def mock_readme_content():
    """Sample README content for testing."""
    return """
    # Test Recipe

    This is a test recipe for reading files.

    ## Usage

    Use this recipe to test file reading functionality.
    """


@pytest.mark.asyncio
@patch("recipe_tool_app.example_handler.get_repo_root")
@patch("recipe_tool_app.example_handler.os.path.exists")
@patch("recipe_tool_app.example_handler.os.path.join")
@patch("recipe_tool_app.example_handler.os.path.dirname")
async def test_load_example_success(
    mock_dirname, mock_join, mock_exists, mock_repo_root, mock_file_content, mock_readme_content
):
    """Test successful loading of an example recipe."""
    # Import here to use the patched modules
    from recipe_tool_app.example_handler import load_example

    # Setup mocks
    mock_repo_root.return_value = "/test/repo"
    mock_join.side_effect = lambda *args: "/".join(args)
    mock_dirname.return_value = "/test/repo/recipes"

    # Path to example file and README
    example_path = "/test/repo/recipes/test_recipe.json"
    readme_path = "/test/repo/recipes/README.md"

    # Make it find both the example file and README
    mock_exists.side_effect = lambda path: path in (example_path, readme_path)

    # Patch open to handle file reads
    with patch("builtins.open", mock_open()) as mocked_open:
        # Configure the mock to return different content for different files
        handle = mocked_open.return_value
        handle.read.side_effect = [mock_file_content, mock_readme_content]

        # Call the function
        result = await load_example(example_path)

        # Verify that open was called with the right files
        open_calls = [args[0] for args, _ in mocked_open.call_args_list]
        assert example_path in open_calls
        assert readme_path in open_calls

    # Assertions
    assert "recipe_content" in result
    assert mock_file_content in result["recipe_content"]
    assert "description" in result
    assert mock_readme_content in result["description"]


@pytest.mark.asyncio
@patch("recipe_tool_app.example_handler.get_repo_root")
@patch("recipe_tool_app.example_handler.os.path.exists")
async def test_load_example_file_not_found(mock_exists, mock_repo_root):
    """Test handling of non-existent example files."""
    # Import here to use the patched modules
    from recipe_tool_app.example_handler import load_example

    # Setup mocks
    mock_repo_root.return_value = "/test/repo"
    mock_exists.return_value = False

    # Call the function
    result = await load_example("/test/repo/recipes/nonexistent.json")

    # Assertions
    assert "recipe_content" in result
    assert result["recipe_content"] == ""
    assert "description" in result
    assert "Error" in result["description"]
    assert "Could not find example recipe" in result["description"]


@pytest.mark.asyncio
@patch("recipe_tool_app.example_handler.get_repo_root")
@patch("recipe_tool_app.example_handler.os.path.exists")
@patch("recipe_tool_app.example_handler.os.path.join")
@patch("builtins.open")
async def test_load_example_with_error(mock_open_func, mock_join, mock_exists, mock_repo_root):
    """Test error handling during example loading."""
    # Import here to use the patched modules
    from recipe_tool_app.example_handler import load_example

    # Setup mocks
    mock_repo_root.return_value = "/test/repo"
    mock_join.side_effect = lambda *args: "/".join(args)
    mock_exists.return_value = True

    # Simulate an IO error
    mock_open_func.side_effect = IOError("Test file read error")

    # Call the function
    result = await load_example("/test/repo/recipes/test_recipe.json")

    # Assertions
    assert "recipe_content" in result
    assert result["recipe_content"] == ""
    assert "description" in result
    assert "Error loading example" in result["description"]
    assert "Test file read error" in result["description"]


@patch("recipe_tool_app.example_handler.os.path.exists")
@patch("recipe_tool_app.example_handler.os.path.isdir")
def test_find_examples_in_directory(mock_isdir, mock_exists):
    """Verify basic functionality of find_examples_in_directory."""
    # Import
    from recipe_tool_app.example_handler import find_examples_in_directory

    # Make the directory check fail
    mock_exists.return_value = False
    mock_isdir.return_value = False

    # Call the function
    results = find_examples_in_directory("/test/examples")

    # Should return an empty dict when directory doesn't exist
    assert isinstance(results, dict)
    assert len(results) == 0


@patch("recipe_tool_app.example_handler.get_repo_root")
@patch("recipe_tool_app.example_handler.os.path.exists")
@patch("recipe_tool_app.example_handler.os.path.isdir")
def test_find_examples_directory_not_found(mock_isdir, mock_exists, mock_repo_root):
    """Test handling of non-existent directories in find_examples_in_directory."""
    # Import here to use the patched modules
    from recipe_tool_app.example_handler import find_examples_in_directory

    # Setup mocks
    mock_repo_root.return_value = "/test/repo"
    mock_exists.return_value = False
    mock_isdir.return_value = False

    # Call the function
    results = find_examples_in_directory("/test/nonexistent")

    # Assertions
    assert isinstance(results, dict)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_load_example_formatted():
    """Test that load_example_formatted correctly formats the result from load_example."""
    # Import here
    from recipe_tool_app.example_handler import load_example_formatted

    # Create a mock for load_example
    with patch("recipe_tool_app.example_handler.load_example") as mock_load:
        mock_load.return_value = {"recipe_content": "test content", "description": "test description"}

        # Call the function
        content, description = await load_example_formatted("test_path")

        # Assertions
        assert content == "test content"
        assert description == "test description"
        mock_load.assert_called_once_with("test_path")
