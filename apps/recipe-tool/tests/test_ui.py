"""Tests for the UI module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from recipe_tool_app.ui_components import create_recipe_ui


@pytest.fixture
def mock_recipe_core():
    """Create a mock RecipeToolCore for testing."""
    core = MagicMock()
    core.create_recipe = AsyncMock(
        return_value={
            "recipe_json": '{"name": "test"}',
            "structure_preview": "Test preview",
            "debug_context": {"test": "context"},
        }
    )
    return core


class TestCreateRecipeUI:
    """Tests for the create_recipe_ui function."""

    @patch("gradio.Row")
    @patch("gradio.Column")
    @patch("gradio.Markdown")
    @patch("gradio.Tabs")
    @patch("gradio.TabItem")
    @patch("gradio.TextArea")
    @patch("gradio.File")
    @patch("gradio.Accordion")
    @patch("gradio.Textbox")
    @patch("gradio.Button")
    @patch("gradio.Code")
    @patch("gradio.JSON")
    @patch("gradio.Dropdown")
    @patch("recipe_tool_app.config.settings")
    def test_create_recipe_ui(
        self,
        mock_settings,
        mock_dropdown,
        mock_json,
        mock_code,
        mock_button,
        mock_textbox,
        mock_accordion,
        mock_file,
        mock_textarea,
        mock_tab_item,
        mock_tabs,
        mock_markdown,
        mock_column,
        mock_row,
        mock_recipe_core,
    ):
        """Test that create_recipe_ui creates the expected UI components."""
        # Setup mock settings with example ideas
        from recipe_tool_app.config import ExampleIdea

        mock_settings.example_ideas = [
            ExampleIdea(name="Test 1", path="test1.md", context_vars={"key": "value"}),
        ]

        # Setup context managers
        for mock in [mock_row, mock_column, mock_tabs, mock_tab_item, mock_accordion]:
            instance = mock.return_value
            instance.__enter__.return_value = instance

        # Call the function
        result = create_recipe_ui(mock_recipe_core)

        # Verify the result is a tuple with the expected components
        assert isinstance(result, tuple)
        assert len(result) == 8

        # Verify that components were created
        assert mock_code.call_count == 2  # idea_text and recipe_output
        assert mock_file.call_count == 2  # idea_file and reference_files
        mock_textbox.assert_called_once()  # context_vars
        assert mock_button.call_count == 2  # create_btn + load_example_btn
        mock_dropdown.assert_called_once()  # example_dropdown
        mock_json.assert_called_once()  # debug_context

        # Verify click events were set up
        assert mock_button.return_value.click.call_count == 2
