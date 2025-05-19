"""Tests for the ui_components module of the recipe_tool_app package."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_recipe_core():
    """Create a mock RecipeToolCore instance."""
    core = MagicMock()
    core.create_recipe = AsyncMock()
    core.create_recipe.return_value = {
        "recipe_json": '{"name": "Test Recipe"}',
        "structure_preview": "### Test Recipe Preview",
        "debug_context": {"generated_recipe": '{"name": "Test Recipe"}'},
    }

    return core


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

    # Verify the function exists and has the right signature
    assert callable(build_ui)

    # Verify that build_ui expects a RecipeToolCore parameter
    import inspect

    sig = inspect.signature(build_ui)
    params = list(sig.parameters.values())
    assert len(params) == 1
    assert params[0].name == "recipe_core"
    assert params[0].annotation == RecipeToolCore
