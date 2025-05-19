"""Integration tests for the recipe_tool_app package."""

from unittest.mock import AsyncMock, MagicMock, mock_open, patch

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
    """Test integration between core and utils modules."""
    # Import
    from recipe_tool_app.core import RecipeToolCore

    # Setup mocks
    mock_dirname.return_value = "/test/path"
    mock_exists.return_value = True

    # Create patches
    with (
        patch("recipe_tool_app.core.prepare_context") as mock_prepare_context,
        patch("recipe_tool_app.core.extract_recipe_content") as mock_extract,
        patch("recipe_tool_app.core.parse_recipe_json") as mock_parse,
    ):
        # Setup mock context
        mock_context = MagicMock()
        mock_context.dict.return_value = {"generated_recipe": '{"name": "Test Recipe", "steps": []}'}
        mock_prepare_context.return_value = ({}, mock_context)

        # Setup mock extraction and parsing
        mock_extract.return_value = '{"name": "Test Recipe", "steps": []}'
        mock_parse.return_value = {"name": "Test Recipe", "steps": []}

        # Further mocks to avoid execution
        with (
            patch("recipe_tool_app.utils.resolve_path") as mock_resolve,
            patch("recipe_tool_app.utils.get_repo_root") as mock_get_root,
            patch("recipe_tool_app.utils.find_recent_json_file") as mock_find,
            patch("recipe_tool_app.core.os.times") as mock_times,
        ):
            mock_resolve.return_value = "/test/path/recipe.json"
            mock_get_root.return_value = "/test/repo"
            mock_find.return_value = (None, None)
            mock_times.return_value = MagicMock(elapsed=1.0)

            # Create a mock for parse_recipe_json
            with patch("recipe_tool_app.utils.parse_recipe_json") as mock_parse:
                # Configure our parse mock to return something meaningful
                mock_parse.return_value = {"name": "Test Recipe", "steps": []}

                # Need to fix the context.dict return value with generated_recipe
                recipe_text = '{"name": "Test Recipe", "steps": []}'
                mock_context.dict.side_effect = [
                    # First return value when preparing context
                    {},
                    # Second return value after execution
                    {"generated_recipe": recipe_text},
                ]

                # Also patch extract_recipe_content directly in core module
                with patch("recipe_tool_app.core.extract_recipe_content") as direct_extract:
                    direct_extract.return_value = recipe_text

                    # Mock file reading in case it tries to read from file
                    with patch("builtins.open", mock_open(read_data=recipe_text)):
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
@patch("recipe_tool_app.example_handler.get_repo_root")
@patch("recipe_tool_app.example_handler.os.path.exists")
async def test_example_handler_to_utils_integration(mock_exists, mock_get_root):
    """Test integration between example_handler and utils modules."""
    # Import
    from recipe_tool_app.example_handler import load_example

    # Setup mocks
    mock_get_root.return_value = "/test/repo"
    mock_exists.side_effect = lambda path: path == "/test/repo/recipes/test.json"

    # Mock file opening
    with patch("builtins.open", MagicMock()) as mock_open:
        # Setup mock file handle
        mock_file = MagicMock()
        mock_file.read.return_value = '{"name": "Test Recipe"}'
        mock_open.return_value.__enter__.return_value = mock_file

        # Call function
        result = await load_example("/test/repo/recipes/test.json")

    # Verify integration
    assert mock_get_root.called  # example_handler called get_repo_root from utils

    # Verify result structure
    assert "recipe_content" in result
    assert "description" in result


@pytest.mark.asyncio
@patch("recipe_tool_app.ui_components.gr")
@patch("recipe_tool_app.ui_components.json")
async def test_ui_to_core_integration(mock_json, mock_gr, mock_executor):
    """Test integration between UI components and core functionality."""
    # Import
    from recipe_tool_app.core import RecipeToolCore
    from recipe_tool_app.ui_components import setup_execute_recipe_events

    # Create a real core instance with mock executor
    core = RecipeToolCore(executor=mock_executor)

    # Mock core's execute_recipe to return predictable results
    core.execute_recipe = AsyncMock()
    core.execute_recipe.return_value = {
        "formatted_results": "Test results",
        "raw_json": '{"test": "value"}',
        "debug_context": {"test": "value"},
    }

    # Mock JSON serialization
    mock_json.dumps.return_value = '{"test": "value"}'

    # Create mock UI components
    file = MagicMock()
    text = MagicMock()
    vars = MagicMock()
    btn = MagicMock()
    output = MagicMock()
    raw = MagicMock()
    debug = MagicMock()

    # Setup the event handler
    setup_execute_recipe_events(core, file, text, vars, btn, output, raw, debug)

    # Get the event handler function
    event_fn = btn.click.call_args[1]["fn"]

    # Call the event handler
    result = await event_fn("test.json", None, "key=value")

    # Verify core method was called
    assert core.execute_recipe.called
    assert core.execute_recipe.call_args[0][0] == "test.json"

    # Verify integration works correctly
    assert result[0] == "Test results"  # Formatted results
    assert result[1] == '{"test": "value"}'  # Raw JSON
    assert result[2] == '{"test": "value"}'  # Debug context
