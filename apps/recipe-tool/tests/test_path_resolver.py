"""Tests for the path_resolver module of the recipe_tool_app package."""

from unittest.mock import patch


from recipe_tool_app.path_resolver import (
    ensure_directory_exists,
    find_file_by_name,
    get_output_directory,
    get_potential_paths,
    get_recipes_directory,
    get_repo_root,
    resolve_path,
)


def test_get_repo_root():
    """Test the get_repo_root function."""
    with patch("os.path.abspath") as mock_abspath:
        # Setup mock
        mock_abspath.return_value = "/test/repo"

        # Call function
        result = get_repo_root()

        # Assertions
        assert result == "/test/repo"
        assert mock_abspath.called


@patch("recipe_tool_app.path_resolver.get_repo_root")
@patch("recipe_tool_app.path_resolver.os.path.isabs")
@patch("recipe_tool_app.path_resolver.os.path.join")
def test_resolve_path_absolute(mock_join, mock_isabs, mock_repo_root):
    """Test resolve_path with an absolute path."""
    # Setup mocks
    mock_isabs.return_value = True
    mock_repo_root.return_value = "/test/repo"

    # Call function
    result = resolve_path("/absolute/path")

    # Assertions
    assert result == "/absolute/path"
    assert not mock_join.called


@patch("recipe_tool_app.path_resolver.get_repo_root")
@patch("recipe_tool_app.path_resolver.os.path.isabs")
@patch("recipe_tool_app.path_resolver.os.path.join")
def test_resolve_path_relative_with_root(mock_join, mock_isabs, mock_repo_root):
    """Test resolve_path with a relative path and specified root."""
    # Setup mocks
    mock_isabs.side_effect = lambda path: path.startswith("/")
    mock_repo_root.return_value = "/test/repo"
    mock_join.side_effect = lambda *args: "/".join(args)

    # Call function with relative path and absolute root
    result = resolve_path("relative/path", root="/custom/root")

    # Assertions
    assert result == "/custom/root/relative/path"
    assert mock_join.called


@patch("recipe_tool_app.path_resolver.get_repo_root")
@patch("recipe_tool_app.path_resolver.os.path.isabs")
@patch("recipe_tool_app.path_resolver.os.path.join")
def test_resolve_path_with_dotdot_prefix(mock_join, mock_isabs, mock_repo_root):
    """Test resolve_path with ../ prefix."""
    # Setup mocks
    mock_isabs.return_value = False
    mock_repo_root.return_value = "/test/repo"
    mock_join.side_effect = lambda *args: "/".join(args)

    # Call function with ../ path
    result = resolve_path("../sibling/file.txt")

    # Expect repo_root's parent directory + sibling/file.txt
    assert "/sibling/file.txt" in result


@patch("recipe_tool_app.path_resolver.get_repo_root")
@patch("recipe_tool_app.path_resolver.os.path.isabs")
@patch("recipe_tool_app.path_resolver.os.path.join")
@patch("recipe_tool_app.path_resolver.os.path.exists")
@patch("recipe_tool_app.path_resolver._attempt_path_fixes")
def test_resolve_path_with_fixes(mock_fixes, mock_exists, mock_join, mock_isabs, mock_repo_root):
    """Test resolve_path with path fixes."""
    # Setup mocks
    mock_isabs.return_value = False
    mock_repo_root.return_value = "/test/repo"
    mock_join.side_effect = lambda *args: "/".join(args)
    mock_exists.return_value = False
    mock_fixes.return_value = "/test/repo/fixed/path.txt"

    # Call function with path that requires fixing
    result = resolve_path("nonexistent/path.txt", attempt_fixes=True)

    # Assertions
    assert result == "/test/repo/fixed/path.txt"
    assert mock_fixes.called


@patch("recipe_tool_app.path_resolver.get_repo_root")
@patch("os.path.exists")
@patch("os.makedirs")
def test_ensure_directory_exists_existing(mock_makedirs, mock_exists, mock_repo_root):
    """Test ensure_directory_exists with an existing directory."""
    # Setup mocks
    mock_exists.return_value = True
    mock_repo_root.return_value = "/test/repo"

    # Call function
    result = ensure_directory_exists("/test/directory")

    # Assertions
    assert result == "/test/directory"
    assert not mock_makedirs.called


@patch("recipe_tool_app.path_resolver.get_repo_root")
@patch("os.path.exists")
@patch("os.makedirs")
def test_ensure_directory_exists_new(mock_makedirs, mock_exists, mock_repo_root):
    """Test ensure_directory_exists with a new directory."""
    # Setup mocks
    mock_exists.return_value = False
    mock_repo_root.return_value = "/test/repo"

    # Call function
    result = ensure_directory_exists("/test/new_directory")

    # Assertions
    assert result == "/test/new_directory"
    assert mock_makedirs.called
    mock_makedirs.assert_called_once_with("/test/new_directory", exist_ok=True)


@patch("recipe_tool_app.path_resolver.get_repo_root")
def test_get_recipes_directory(mock_repo_root):
    """Test get_recipes_directory function."""
    # Setup mock
    mock_repo_root.return_value = "/test/repo"

    # Call function
    result = get_recipes_directory()

    # Assertions
    assert result == "/test/repo/recipes"


@patch("recipe_tool_app.path_resolver.get_repo_root")
@patch("recipe_tool_app.path_resolver.ensure_directory_exists")
def test_get_output_directory(mock_ensure_dir, mock_repo_root):
    """Test get_output_directory function."""
    # Setup mocks
    mock_repo_root.return_value = "/test/repo"
    mock_ensure_dir.side_effect = lambda x: x

    # Call function
    result = get_output_directory()

    # Assertions
    assert result == "/test/repo/output"
    assert mock_ensure_dir.called


@patch("recipe_tool_app.path_resolver.get_repo_root")
def test_get_potential_paths(mock_repo_root):
    """Test get_potential_paths function."""
    # Setup mock
    mock_repo_root.return_value = "/test/repo"

    # Call function
    result = get_potential_paths("example/path.json")

    # Assertions
    assert len(result) == 5
    assert "example/path.json" in result[0]  # Direct path
    assert "/test/repo/example/path.json" in result[1]  # Relative to repo root
    assert "/test/repo/recipes/path.json" in result[4]  # Basename in recipes dir


@patch("recipe_tool_app.path_resolver.os.path.exists")
@patch("os.walk")
def test_find_file_by_name_recursive(mock_walk, mock_exists):
    """Test find_file_by_name with recursive search."""
    # Setup mocks
    mock_exists.return_value = True
    mock_walk.return_value = [
        ("/test/dir", ["subdir"], ["file1.txt"]),
        ("/test/dir/subdir", [], ["target.txt"]),
    ]

    # Call function
    result = find_file_by_name("target.txt", "/test/dir", recursive=True)

    # Assertions
    assert result == "/test/dir/subdir/target.txt"


def test_find_file_by_name_nonrecursive():
    """Test find_file_by_name with non-recursive search."""
    # Create patches
    with patch("os.path.exists") as mock_exists, patch("os.path.join") as mock_join:
        # Need to patch at module level and also at the os.path level
        with (
            patch("recipe_tool_app.path_resolver.os.path.exists", mock_exists),
            patch("recipe_tool_app.path_resolver.os.path.join", mock_join),
        ):
            # Setup mock to return True for the directory and the target file
            mock_exists.side_effect = lambda path: True
            mock_join.return_value = "/test/dir/target.txt"

            # Call function
            result = find_file_by_name("target.txt", "/test/dir", recursive=False)

            # Assertions
            assert result == "/test/dir/target.txt"


@patch("recipe_tool_app.path_resolver.os.path.exists")
def test_find_file_by_name_not_found(mock_exists):
    """Test find_file_by_name when file is not found."""
    # Setup mock
    mock_exists.return_value = False

    # Call function
    result = find_file_by_name("nonexistent.txt", "/test/dir")

    # Assertions
    assert result is None
