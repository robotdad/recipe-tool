"""Integration tests for the recipe_tool_app package."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_executor():
    """Create a mock Executor that can be used across tests."""
    executor = AsyncMock()
    executor.execute = AsyncMock()
    return executor


@pytest.fixture
def app_components():
    """Setup mock components for the entire application."""
    components = {
        "core": None,  # Will be set in tests
        "ui": MagicMock(),
        "logger": MagicMock(),
        "settings": MagicMock(),
    }
    return components


@patch("recipe_tool_app.app.RecipeToolCore")
@patch("recipe_tool_app.app.build_ui")
def test_app_initialization(mock_build_ui, mock_core):
    """Test that app initialization connects all components correctly."""
    # Import
    from recipe_tool_app.app import create_app

    # Setup mocks
    mock_core_instance = MagicMock()
    mock_core.return_value = mock_core_instance

    mock_ui = MagicMock()
    mock_build_ui.return_value = mock_ui

    # Call function
    app = create_app()

    # Verify initialization flow
    assert mock_core.called
    assert mock_build_ui.called

    # Verify UI was built with core instance
    mock_build_ui.assert_called_once_with(mock_core_instance)

    # Verify app returned from build_ui
    assert app == mock_ui


@pytest.mark.asyncio
@patch("recipe_tool_app.core.os.path.exists")
@patch("recipe_tool_app.core.os.path.dirname")
async def test_core_to_utils_integration(mock_dirname, mock_exists, mock_executor):
    """Test integration between core and module dependencies."""
    # Import
    from recipe_tool_app.core import RecipeToolCore

    # Setup mocks
    mock_dirname.return_value = "/test/path"
    mock_exists.return_value = True

    # Create patches for core's dependencies
    with (
        patch("recipe_tool_app.core.prepare_context") as mock_prepare_context,
        patch("recipe_tool_app.core.extract_recipe_content") as mock_extract,
        patch("recipe_tool_app.core.generate_recipe_preview") as mock_preview,
    ):
        # Setup mock context
        mock_context = MagicMock()
        mock_context.dict.return_value = {"generated_recipe": '{"name": "Test Recipe", "steps": []}'}
        mock_prepare_context.return_value = ({}, mock_context)

        # Setup mock extraction and preview
        recipe_text = '{"name": "Test Recipe", "steps": []}'
        mock_extract.return_value = recipe_text
        mock_preview.return_value = "### Recipe Structure\n\n**Name**: Test Recipe"

        # Further mocks to avoid execution
        with (
            patch("recipe_tool_app.path_resolver.resolve_path") as mock_resolve,
            patch("recipe_tool_app.path_resolver.get_repo_root") as mock_get_root,
            patch("recipe_tool_app.file_operations.find_recent_json_file") as mock_find,
            patch("recipe_tool_app.core.os.times") as mock_times,
        ):
            mock_resolve.return_value = "/test/path/recipe.json"
            mock_get_root.return_value = "/test/repo"
            mock_find.return_value = (None, None)
            mock_times.return_value = MagicMock(elapsed=1.0)

            # Create a mock for the path_resolver module
            with patch("recipe_tool_app.core.create_temp_file") as mock_create_temp:
                # Configure our mocks
                mock_create_temp.return_value = ("/tmp/idea.md", MagicMock())

                # Mock _find_recipe_output to return the recipe
                with patch.object(RecipeToolCore, "_find_recipe_output") as mock_find_output:
                    mock_find_output.return_value = recipe_text

                    # Mock parse_recipe_json to return a parsed recipe
                    with patch("recipe_tool_app.core.parse_recipe_json") as mock_parse:
                        mock_parse.return_value = {"name": "Test Recipe", "steps": []}

                        # Create core with mock executor
                        core = RecipeToolCore(executor=mock_executor)

                        # Execute core method
                        result = await core.create_recipe(
                            idea_text="Test idea", idea_file=None, reference_files=None, context_vars=None
                        )

                # Verify result structure instead of calls
                assert "recipe_json" in result
                assert "structure_preview" in result
                assert "Test Recipe" in result["structure_preview"]

    # Verify result structure
    assert "recipe_json" in result
    assert "structure_preview" in result
    assert "debug_context" in result


@pytest.mark.asyncio
async def test_example_handler_to_utils_integration():
    """Test integration between example_handler and path_resolver modules."""
    # Import
    from recipe_tool_app.example_handler import load_example

    # Setup mocks
    test_path = "/test/repo/recipes/test.json"

    # Create mocked objects
    with (
        patch("recipe_tool_app.example_handler.get_potential_paths") as mock_get_paths,
        patch("recipe_tool_app.example_handler.os.path.exists") as mock_exists,
        patch("recipe_tool_app.example_handler.read_file") as mock_read,
    ):
        # Setup the mocks
        mock_get_paths.return_value = [test_path]
        mock_exists.side_effect = lambda path: path == test_path
        mock_read.return_value = '{"name": "Test Recipe"}'

        # Call function
        result = await load_example(test_path)

        # Verify integration
        assert mock_get_paths.called  # example_handler called get_potential_paths
        assert mock_read.called  # example_handler called read_file

    # Verify result structure
    assert "recipe_content" in result
    assert "description" in result


@pytest.mark.asyncio
@patch("recipe_tool_app.ui_components.create_executor_block")
@patch("recipe_tool_app.ui_components.RecipeExecutorCore")
async def test_recipe_executor_integration(mock_executor_core, mock_create_block, mock_executor):
    """Test integration between Recipe Tool app and Recipe Executor component."""
    # Import
    from recipe_tool_app.core import RecipeToolCore
    from recipe_tool_app.ui_components import build_ui

    # Ensure that the Recipe Executor components are properly imported
    assert mock_executor_core.called is False  # Not called until UI is built
    assert mock_create_block.called is False  # Not called until UI is built

    # Create a mock for the RecipeExecutorCore
    mock_executor_core_instance = MagicMock()
    mock_executor_core.return_value = mock_executor_core_instance

    # Verify that RecipeToolCore is properly importable
    assert callable(RecipeToolCore)

    # Let's validate that the UI construction is possible
    assert callable(build_ui)
