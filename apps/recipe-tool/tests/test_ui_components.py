"""Tests for the ui_components module of the recipe_tool_app package."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_recipe_core():
    """Create a mock RecipeToolCore instance."""
    core = MagicMock()
    core.execute_recipe = AsyncMock()
    core.execute_recipe.return_value = {
        "formatted_results": "Test results",
        "raw_json": '{"key": "value"}',
        "debug_context": {"key": "value"},
    }

    core.create_recipe = AsyncMock()
    core.create_recipe.return_value = {
        "recipe_json": '{"name": "Test Recipe"}',
        "structure_preview": "### Test Recipe Preview",
        "debug_context": {"generated_recipe": '{"name": "Test Recipe"}'},
    }

    return core


@pytest.fixture
def mock_gradio_components():
    """Create mock Gradio components."""
    return {
        "file": MagicMock(),
        "text": MagicMock(),
        "context_vars": MagicMock(),
        "button": MagicMock(),
        "output": MagicMock(),
        "raw_output": MagicMock(),
        "debug_output": MagicMock(),
    }


@patch("recipe_tool_app.ui_components.gr")
def test_build_execute_recipe_tab(mock_gr):
    """Test building the execute recipe tab."""
    # Mock TabItem context manager
    mock_tab = MagicMock()
    mock_gr.TabItem.return_value.__enter__.return_value = mock_tab

    # Mock UI components
    mock_file = MagicMock()
    mock_text = MagicMock()
    mock_vars = MagicMock()
    mock_btn = MagicMock()
    mock_results = MagicMock()
    mock_raw = MagicMock()
    mock_debug = MagicMock()

    # Setup component returns
    mock_gr.File.return_value = mock_file
    mock_gr.Code.return_value = mock_text
    mock_gr.Textbox.return_value = mock_vars
    mock_gr.Button.return_value = mock_btn
    mock_gr.Markdown.return_value = mock_results

    # Simulate multiple Code returns
    mock_gr.Code.side_effect = [mock_text, mock_raw, mock_debug]

    # Import and call function
    from recipe_tool_app.ui_components import build_execute_recipe_tab

    # Mock additional context managers
    with (
        patch("recipe_tool_app.ui_components.gr.Row") as mock_row,
        patch("recipe_tool_app.ui_components.gr.Column") as mock_col,
        patch("recipe_tool_app.ui_components.gr.Accordion") as mock_acc,
        patch("recipe_tool_app.ui_components.gr.Tabs") as mock_tabs,
    ):
        mock_row.return_value.__enter__.return_value = MagicMock()
        mock_col.return_value.__enter__.return_value = MagicMock()
        mock_acc.return_value.__enter__.return_value = MagicMock()
        mock_tabs.return_value.__enter__.return_value = MagicMock()

        result = build_execute_recipe_tab()

    # Assertions - verify all components are returned
    assert len(result) == 7
    assert result[0] == mock_file  # recipe_file
    assert result[1] == mock_text  # recipe_text
    assert result[2] == mock_vars  # context_vars
    assert result[3] == mock_btn  # execute_btn
    assert result[4] == mock_results  # result_output
    # mock_raw and mock_debug would be checked similarly


@pytest.mark.asyncio
@patch("recipe_tool_app.ui_components.json")
async def test_execute_recipe_formatted(mock_json, mock_recipe_core):
    """Test the execute_recipe_formatted function."""
    # Import
    from recipe_tool_app.ui_components import setup_execute_recipe_events

    # Mock components
    components = {
        "file": MagicMock(),
        "text": MagicMock(),
        "vars": MagicMock(),
        "btn": MagicMock(),
        "output": MagicMock(),
        "raw": MagicMock(),
        "debug": MagicMock(),
    }

    # Mock JSON dumps for debug_context
    mock_json.dumps.return_value = '{"key": "value"}'

    # Setup the click handler
    with patch("recipe_tool_app.ui_components.gr"):
        setup_execute_recipe_events(
            mock_recipe_core,
            components["file"],
            components["text"],
            components["vars"],
            components["btn"],
            components["output"],
            components["raw"],
            components["debug"],
        )

        # Get the click handler function
        click_fn = components["btn"].click.call_args[1]["fn"]

        # Call the click handler
        result = await click_fn("test.json", None, "key=value")

        # Verify core method was called with correct arguments
        mock_recipe_core.execute_recipe.assert_called_once_with("test.json", None, "key=value")

        # Verify result is formatted correctly for UI
        assert result[0] == "Test results"
        assert result[1] == '{"key": "value"}'
        assert mock_json.dumps.called


@pytest.mark.asyncio
@patch("recipe_tool_app.ui_components.json")
async def test_create_recipe_formatted(mock_json, mock_recipe_core):
    """Test the create_recipe_formatted function."""
    # Import
    from recipe_tool_app.ui_components import setup_create_recipe_events

    # Mock components
    components = {
        "idea_text": MagicMock(),
        "idea_file": MagicMock(),
        "ref_files": MagicMock(),
        "vars": MagicMock(),
        "btn": MagicMock(),
        "output": MagicMock(),
        "preview": MagicMock(),
        "debug": MagicMock(),
    }

    # Mock JSON dumps for debug_context
    mock_json.dumps.return_value = '{"generated_recipe": "test"}'

    # Setup the click handler
    with patch("recipe_tool_app.ui_components.gr"):
        setup_create_recipe_events(
            mock_recipe_core,
            components["idea_text"],
            components["idea_file"],
            components["ref_files"],
            components["vars"],
            components["btn"],
            components["output"],
            components["preview"],
            components["debug"],
        )

        # Get the click handler function
        click_fn = components["btn"].click.call_args[1]["fn"]

        # Call the click handler
        result = await click_fn("Test idea", None, ["ref1.md"], "key=value")

        # Verify core method was called with correct arguments
        mock_recipe_core.create_recipe.assert_called_once_with("Test idea", None, ["ref1.md"], "key=value")

        # Verify result is formatted correctly for UI
        assert result[0] == '{"name": "Test Recipe"}'
        assert result[1] == "### Test Recipe Preview"
        assert mock_json.dumps.called


def test_build_ui():
    """Test the most basic aspects of the build_ui function."""
    # Import
    from recipe_tool_app.core import RecipeToolCore
    from recipe_tool_app.ui_components import build_ui

    # Instead of testing the whole UI, just verify the function exists and has the right signature
    assert callable(build_ui)

    # Verify that build_ui expects a RecipeToolCore parameter
    import inspect

    sig = inspect.signature(build_ui)
    params = list(sig.parameters.values())
    assert len(params) == 1
    assert params[0].name == "recipe_core"
    assert params[0].annotation == RecipeToolCore
