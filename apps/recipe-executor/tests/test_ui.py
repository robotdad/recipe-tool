"""Tests for the UI module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from recipe_executor_app.ui import create_ui, create_examples_ui


@pytest.fixture
def mock_recipe_core():
    """Create a mock RecipeExecutorCore for testing."""
    core = MagicMock()
    core.execute_recipe = AsyncMock(
        return_value={
            "formatted_results": "Test results",
            "raw_json": '{"result": "test"}',
            "debug_context": {"result": "test"},
        }
    )
    core.load_recipe = AsyncMock(
        return_value={
            "recipe_content": '{"steps": []}',
            "structure_preview": "Test preview",
        }
    )
    return core


class TestCreateUI:
    """Tests for the create_ui function."""

    @patch("gradio.Row")
    @patch("gradio.Column")
    @patch("gradio.Markdown")
    @patch("gradio.File")
    @patch("gradio.Code")
    @patch("gradio.Accordion")
    @patch("gradio.Textbox")
    @patch("gradio.Button")
    @patch("gradio.Tabs")
    @patch("gradio.TabItem")
    @patch("gradio.JSON")
    def test_create_ui(
        self,
        mock_json,
        mock_tab_item,
        mock_tabs,
        mock_button,
        mock_textbox,
        mock_accordion,
        mock_code,
        mock_file,
        mock_markdown,
        mock_column,
        mock_row,
        mock_recipe_core,
    ):
        """Test that create_ui creates the expected UI components."""
        # Setup context managers
        for mock in [mock_row, mock_column, mock_accordion, mock_tabs, mock_tab_item]:
            instance = mock.return_value
            instance.__enter__.return_value = instance

        # Call the function
        result = create_ui(mock_recipe_core)

        # Verify the result is a tuple with the expected components
        assert isinstance(result, tuple)
        assert len(result) == 7

        # Verify that components were created
        mock_file.assert_called_once()
        mock_code.assert_called()
        mock_textbox.assert_called()
        mock_button.assert_called_once()
        mock_markdown.assert_called()
        mock_json.assert_called_once()


class TestCreateExamplesUI:
    """Tests for the create_examples_ui function."""

    @patch("gradio.Dropdown")
    @patch("gradio.Button")
    @patch("gradio.Markdown")
    @patch("recipe_executor_app.config.settings")
    def test_create_examples_ui(self, mock_settings, mock_markdown, mock_button, mock_dropdown, mock_recipe_core):
        """Test that create_examples_ui creates the expected UI components."""
        # Setup mock settings with ExampleRecipe objects
        from recipe_executor_app.config import ExampleRecipe

        mock_settings.example_recipes = [
            ExampleRecipe(name="Test 1", path="test1.json", context_vars={"key": "value"}),
            ExampleRecipe(name="Test 2", path="test2.json", context_vars={}),
        ]

        # Setup mock components
        recipe_text = MagicMock()
        context_vars = MagicMock()

        # Call the function
        result = create_examples_ui(mock_recipe_core, recipe_text, context_vars)

        # Verify the result is a tuple with the expected components
        assert isinstance(result, tuple)
        assert len(result) == 3

        # Verify that components were created
        mock_dropdown.assert_called_once()
        mock_button.assert_called_once()
        mock_markdown.assert_called_once()

        # Verify click event was set up
        mock_button.return_value.click.assert_called_once()
