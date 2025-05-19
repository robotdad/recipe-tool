"""Tests for the utils module of the recipe_tool_app package."""

from unittest.mock import mock_open, patch


@patch("recipe_tool_app.utils.os.path.abspath")
def test_get_repo_root(mock_abspath):
    """Test the get_repo_root function."""
    # Setup mock
    mock_abspath.return_value = "/test/repo"

    # Import and call function
    from recipe_tool_app.utils import get_repo_root

    result = get_repo_root()

    # Assertions
    assert result == "/test/repo"
    assert mock_abspath.called


@patch("recipe_tool_app.utils.get_repo_root")
@patch("recipe_tool_app.utils.os.path.isabs")
@patch("recipe_tool_app.utils.os.path.join")
def test_resolve_path_absolute(mock_join, mock_isabs, mock_repo_root):
    """Test resolve_path with an absolute path."""
    # Import
    from recipe_tool_app.utils import resolve_path

    # Setup mocks
    mock_isabs.return_value = True
    mock_repo_root.return_value = "/test/repo"

    # Call function
    result = resolve_path("/absolute/path")

    # Assertions
    assert result == "/absolute/path"
    assert not mock_join.called


@patch("recipe_tool_app.utils.get_repo_root")
@patch("recipe_tool_app.utils.os.path.isabs")
@patch("recipe_tool_app.utils.os.path.join")
def test_resolve_path_relative_with_root(mock_join, mock_isabs, mock_repo_root):
    """Test resolve_path with a relative path and specified root."""
    # Import
    from recipe_tool_app.utils import resolve_path

    # Setup mocks
    mock_isabs.side_effect = lambda path: path.startswith("/")
    mock_repo_root.return_value = "/test/repo"
    mock_join.side_effect = lambda *args: "/".join(args)

    # Call function with relative path and absolute root
    result = resolve_path("relative/path", root="/custom/root")

    # Assertions
    assert result == "/custom/root/relative/path"
    assert mock_join.called


@patch("recipe_tool_app.utils.get_repo_root")
@patch("recipe_tool_app.utils.os.path.isabs")
@patch("recipe_tool_app.utils.os.path.join")
@patch("recipe_tool_app.utils.os.path.exists")
@patch("recipe_tool_app.utils.os.walk")
def test_resolve_path_with_fallbacks(mock_walk, mock_exists, mock_join, mock_isabs, mock_repo_root):
    """Test resolve_path with fallback path resolution."""
    # Import
    from recipe_tool_app.utils import resolve_path

    # Setup mocks
    mock_isabs.return_value = False
    mock_repo_root.return_value = "/test/repo"
    mock_join.side_effect = lambda *args: "/".join(args)

    # First resolved path doesn't exist, but fallback does
    mock_exists.side_effect = lambda path: path == "/test/repo/recipes/file.txt"

    # Mock os.walk to find the file
    mock_walk.return_value = [("/test/repo/recipes", [], ["file.txt"])]

    # Call function with path that requires fallback
    result = resolve_path("file.txt", attempt_fixes=True)

    # Assertions
    assert result == "/test/repo/recipes/file.txt"


def test_extract_recipe_content_string():
    """Test extract_recipe_content with a string input."""
    # Import
    from recipe_tool_app.utils import extract_recipe_content

    # Test with string
    result = extract_recipe_content('{"name": "Test Recipe"}')

    # Assertions
    assert result == '{"name": "Test Recipe"}'


def test_extract_recipe_content_list():
    """Test extract_recipe_content with a list input."""
    # Import
    from recipe_tool_app.utils import extract_recipe_content

    # Test with list containing dict with content
    input_list = [{"content": '{"name": "Test Recipe"}', "path": "test.json"}]
    result = extract_recipe_content(input_list)

    # Assertions
    assert result == '{"name": "Test Recipe"}'


def test_extract_recipe_content_dict():
    """Test extract_recipe_content with a dictionary input."""
    # Import
    from recipe_tool_app.utils import extract_recipe_content

    # Test with dict with content
    input_dict = {"content": '{"name": "Test Recipe"}', "path": "test.json"}
    result = extract_recipe_content(input_dict)

    # Assertions
    assert result == '{"name": "Test Recipe"}'


def test_extract_recipe_content_none():
    """Test extract_recipe_content with invalid inputs."""
    # Import
    from recipe_tool_app.utils import extract_recipe_content

    # Test with various invalid inputs
    assert extract_recipe_content(None) is None
    assert extract_recipe_content([]) is None
    assert extract_recipe_content([{"no_content": "value"}]) is None
    assert extract_recipe_content({"no_content": "value"}) is None


@patch("recipe_tool_app.utils.os.path.exists")
@patch("recipe_tool_app.utils.os.listdir")
@patch("recipe_tool_app.utils.os.path.getmtime")
@patch("recipe_tool_app.utils.time.time")
def test_find_recent_json_file_success(mock_time, mock_getmtime, mock_listdir, mock_exists):
    """Test find_recent_json_file when a recent file exists."""
    # Import
    from recipe_tool_app.utils import find_recent_json_file

    # Setup mocks
    mock_exists.return_value = True
    mock_listdir.return_value = ["file1.json", "file2.txt", "file3.json"]
    mock_getmtime.side_effect = lambda path: 100 if "file3.json" in path else 90
    mock_time.return_value = 110  # current time

    # Mock file reading
    with patch("builtins.open", mock_open(read_data='{"name": "Test"}')):
        # Call function
        content, path = find_recent_json_file("/test/dir")

    # Assertions
    assert content == '{"name": "Test"}'
    assert path is not None and "file3.json" in path


@patch("recipe_tool_app.utils.os.path.exists")
def test_find_recent_json_file_missing_dir(mock_exists):
    """Test find_recent_json_file when directory doesn't exist."""
    # Import
    from recipe_tool_app.utils import find_recent_json_file

    # Setup mocks
    mock_exists.return_value = False

    # Call function
    content, path = find_recent_json_file("/nonexistent/dir")

    # Assertions
    assert content is None
    assert path is None


@patch("recipe_tool_app.utils.os.path.exists")
@patch("recipe_tool_app.utils.os.listdir")
def test_find_recent_json_file_no_files(mock_listdir, mock_exists):
    """Test find_recent_json_file when no JSON files exist."""
    # Import
    from recipe_tool_app.utils import find_recent_json_file

    # Setup mocks
    mock_exists.return_value = True
    mock_listdir.return_value = ["file1.txt", "file2.py"]

    # Call function
    content, path = find_recent_json_file("/test/dir")

    # Assertions
    assert content is None
    assert path is None


@patch("recipe_tool_app.utils.os.path.exists")
@patch("recipe_tool_app.utils.os.listdir")
@patch("recipe_tool_app.utils.os.path.getmtime")
@patch("recipe_tool_app.utils.time.time")
def test_find_recent_json_file_too_old(mock_time, mock_getmtime, mock_listdir, mock_exists):
    """Test find_recent_json_file when files are too old."""
    # Import
    from recipe_tool_app.utils import find_recent_json_file

    # Setup mocks
    mock_exists.return_value = True
    mock_listdir.return_value = ["file1.json"]
    mock_getmtime.return_value = 50  # file modification time
    mock_time.return_value = 120  # current time (70 seconds later)

    # Call function with 30-second max age
    content, path = find_recent_json_file("/test/dir", max_age_seconds=30)

    # Assertions
    assert content is None
    assert path is None


def test_parse_recipe_json_valid():
    """Test parse_recipe_json with valid JSON string."""
    # Import
    from recipe_tool_app.utils import parse_recipe_json

    # Test with valid JSON
    valid_json = '{"name": "Test Recipe", "steps": []}'
    result = parse_recipe_json(valid_json)

    # Assertions
    assert isinstance(result, dict)
    assert result["name"] == "Test Recipe"
    assert result["steps"] == []


def test_parse_recipe_json_dict_input():
    """Test parse_recipe_json with dictionary input."""
    # Import
    from recipe_tool_app.utils import parse_recipe_json

    # Test with dict input
    dict_input = {"name": "Test Recipe", "steps": []}
    # Convert dict to JSON string since parse_recipe_json expects a string
    import json
    json_input = json.dumps(dict_input)
    result = parse_recipe_json(json_input)

    # Assertions
    assert isinstance(result, dict)
    assert result["name"] == "Test Recipe"
    assert result["steps"] == []


def test_parse_recipe_json_empty():
    """Test parse_recipe_json with empty input."""
    # Import
    from recipe_tool_app.utils import parse_recipe_json

    # Test with empty input
    result = parse_recipe_json("")

    # Assertions
    assert isinstance(result, dict)
    assert result == {}
