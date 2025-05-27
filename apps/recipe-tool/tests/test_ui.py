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
    def test_create_recipe_ui(
        self,
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
        mock_textarea.assert_called_once()  # idea_text
        assert mock_file.call_count == 2  # idea_file and reference_files
        mock_textbox.assert_called_once()  # context_vars
        mock_button.assert_called_once()  # create_btn
        mock_code.assert_called_once()  # recipe_output
        mock_json.assert_called_once()  # debug_context

        # Verify click event was set up
        mock_button.return_value.click.assert_called_once()
