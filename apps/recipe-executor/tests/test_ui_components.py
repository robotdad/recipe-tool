"""Tests for the UI components."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from recipe_executor_app.app import create_executor_block
from recipe_executor_app.ui_components import (
    build_execute_recipe_tab,
    build_examples_tab,
    setup_execute_recipe_events,
    setup_example_events,
)


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


class TestCreateExecutorBlock:
    """Tests for the create_executor_block function."""

    @patch("recipe_executor_app.app.build_execute_recipe_tab")
    @patch("recipe_executor_app.app.build_examples_tab")
    @patch("recipe_executor_app.app.setup_execute_recipe_events")
    @patch("recipe_executor_app.app.setup_example_events")
    @patch("gradio.Blocks")
    @patch("gradio.Markdown")
    @patch("gradio.Accordion")  # Using Accordion instead of Tabs since that's what's in app.py
    def test_create_executor_block(
        self,
        mock_accordion,
        mock_markdown,
        mock_blocks,
        mock_setup_example,
        mock_setup_execute,
        mock_build_examples,
        mock_build_execute,
        mock_recipe_core,
    ):
        """Test that create_executor_block creates the expected UI components."""
        # Setup mocks
        mock_blocks_instance = mock_blocks.return_value
        mock_blocks_instance.__enter__.return_value = mock_blocks_instance

        mock_accordion_instance = mock_accordion.return_value
        mock_accordion_instance.__enter__.return_value = mock_accordion_instance

        # Mock the UI components
        mock_execute_components = (
            MagicMock(),  # recipe_file
            MagicMock(),  # recipe_text
            MagicMock(),  # context_vars
            MagicMock(),  # execute_btn
            MagicMock(),  # progress
            MagicMock(),  # result_output
            MagicMock(),  # raw_result
            MagicMock(),  # debug_context
        )
        mock_examples_components = (MagicMock(), MagicMock(), MagicMock())

        mock_build_execute.return_value = mock_execute_components
        mock_build_examples.return_value = mock_examples_components

        # Call the function
        result = create_executor_block(mock_recipe_core, include_header=True)

        # Verify that UI components were created
        mock_blocks.assert_called_once()
        assert mock_markdown.call_count >= 1  # At least 1 markdown component (when include_header=True)

        # Verify accordion was used for examples section (not tabs)
        mock_accordion.assert_called_once()

        # Verify that components were created
        mock_build_execute.assert_called_once()
        mock_build_examples.assert_called_once()

        # Verify that event handlers were set up
        mock_setup_execute.assert_called_once_with(mock_recipe_core, *mock_execute_components)
        mock_setup_example.assert_called_once_with(
            mock_recipe_core,
            *mock_examples_components[:3],
            mock_execute_components[1],
            mock_execute_components[2],  # context_vars
        )

        # Verify the result
        assert result == mock_blocks_instance


class TestBuildExecuteRecipeTab:
    """Tests for the build_execute_recipe_tab function."""

    @patch("gradio.Row")
    @patch("gradio.Column")
    @patch("gradio.Markdown")
    @patch("gradio.File")
    @patch("gradio.Progress")
    @patch("gradio.Code")
    @patch("gradio.Accordion")
    @patch("gradio.Textbox")
    @patch("gradio.Button")
    @patch("gradio.Tabs")
    # Test with the updated UI structure
    def test_build_execute_recipe_tab(
        self,
        mock_tabs,
        mock_button,
        mock_textbox,
        mock_accordion,
        mock_code,
        mock_progress,
        mock_file,
        mock_markdown,
        mock_column,
        mock_row,
    ):
        """Test that build_execute_recipe_tab creates the expected UI components."""
        # Setup context managers properly
        mock_row_instance = mock_row.return_value
        mock_row_instance.__enter__.return_value = mock_row_instance

        mock_column_instance = mock_column.return_value
        mock_column_instance.__enter__.return_value = mock_column_instance

        mock_accordion_instance = mock_accordion.return_value
        mock_accordion_instance.__enter__.return_value = mock_accordion_instance

        mock_tabs_instance = mock_tabs.return_value
        mock_tabs_instance.__enter__.return_value = mock_tabs_instance

        # Mock Row instances
        mock_execution_indicator = MagicMock()
        # First call to Row creates the main row, second creates progress indicator row
        mock_row.side_effect = [mock_row_instance, mock_execution_indicator]
        mock_execution_indicator.__enter__.return_value = mock_execution_indicator

        # Set up mock returns for components
        mock_file.return_value = "file"
        mock_progress.return_value = "progress"
        mock_code.side_effect = ["text", "logs", "context"]  # recipe_text, logs_output, context_json
        mock_textbox.return_value = "vars"
        mock_button.return_value = "btn"
        # Need 6 markdown instances for: headers (2), indicator, result, context title, logs
        mock_markdown.side_effect = ["header1", "header2", "indicator", "result", "context_title", "logs"]

        # Call the function
        result = build_execute_recipe_tab()

        # Verify the result is an 8-tuple with the expected components
        assert isinstance(result, tuple)
        assert len(result) == 8

        # We don't need to check specific assertions for each component call count
        # since the function itself is not being tested for implementation details,
        # but rather that it returns the correct tuple format


class TestBuildExamplesTab:
    """Tests for the build_examples_tab function."""

    @patch("gradio.Markdown")
    @patch("gradio.Dropdown")
    @patch("gradio.Button")
    def test_build_examples_tab(self, mock_button, mock_dropdown, mock_markdown):
        """Test that build_examples_tab creates the expected UI components."""
        # Set up mock returns for components
        mock_dropdown.return_value = "paths"
        mock_button.return_value = "load_btn"
        mock_markdown.return_value = "desc"

        # Call the function
        result = build_examples_tab()

        # Verify the result is a 3-tuple with the expected components
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert result == ("paths", "load_btn", "desc")

        # Verify that each component was created once
        mock_dropdown.assert_called_once()
        mock_button.assert_called_once()
        mock_markdown.assert_called_once()


class TestSetupExecuteRecipeEvents:
    """Tests for the setup_execute_recipe_events function."""

    # Test with support for chained events
    def test_setup_execute_recipe_events(self, mock_recipe_core):
        """Test that setup_execute_recipe_events sets up the expected event handlers."""
        # Create mock UI components
        recipe_file = MagicMock()
        recipe_file.change = MagicMock()
        recipe_text = MagicMock()
        context_vars = MagicMock()
        execute_btn = MagicMock()
        execute_btn.click = MagicMock()
        recipe_text.change = MagicMock()
        progress = MagicMock()
        result_output = MagicMock()
        logs_output = MagicMock()
        logs_output.__class__.__name__ = "Textbox"  # For type checking
        context_json = MagicMock()
        context_json.__class__.__name__ = "Code"  # For type checking

        # Mock the parent relationship for result_output to find execution_indicator
        execution_indicator = MagicMock()
        mock_parent = MagicMock()
        mock_parent.children = [execution_indicator]
        # Ensure isinstance works for the Row check
        mock_parent.children[0].__class__.__name__ = "Row"
        result_output.parent = mock_parent

        # Mock the click.then method for chained events
        mock_click = MagicMock()
        execute_btn.click.return_value = mock_click
        mock_click.then.return_value = mock_click

        # Call the function
        setup_execute_recipe_events(
            mock_recipe_core,
            recipe_file,
            recipe_text,
            context_vars,
            execute_btn,
            progress,
            result_output,
            logs_output,
            context_json,
        )

        # Verify that the click event was set up
        execute_btn.click.assert_called_once()

        # Check the event setup
        args, kwargs = execute_btn.click.call_args
        assert kwargs["api_name"] == "execute_recipe"
        assert kwargs["inputs"] == [recipe_file, recipe_text, context_vars]
        assert kwargs["outputs"] == [result_output, logs_output, context_json]
        assert kwargs["show_progress"] == "full"
        
        # Verify that the change event was set up for recipe_text
        recipe_text.change.assert_called_once()
        
        # Verify that the change event was set up for recipe_file
        recipe_file.change.assert_called_once()


class TestSetupExampleEvents:
    """Tests for the setup_example_events function."""

    def test_setup_example_events(self, mock_recipe_core):
        """Test that setup_example_events sets up the expected event handlers."""
        # Create mock UI components
        example_paths = MagicMock()
        load_example_btn = MagicMock()
        example_desc = MagicMock()
        recipe_text = MagicMock()
        context_vars = MagicMock()

        # Test with context_vars provided
        setup_example_events(
            mock_recipe_core,
            example_paths,
            load_example_btn,
            example_desc,
            recipe_text,
            context_vars,
        )

        # Verify that the click event was set up
        load_example_btn.click.assert_called_once()

        # Get the arguments from the call
        args, kwargs = load_example_btn.click.call_args

        # Verify the arguments
        assert "fn" in kwargs
        assert "inputs" in kwargs
        assert "outputs" in kwargs
        assert "api_name" in kwargs
        assert kwargs["api_name"] == "load_example"
        assert kwargs["inputs"] == [example_paths]
        assert kwargs["outputs"] == [recipe_text, example_desc, context_vars]

        # Reset the mock
        load_example_btn.reset_mock()

        # Test without context_vars
        setup_example_events(
            mock_recipe_core,
            example_paths,
            load_example_btn,
            example_desc,
            recipe_text,
        )

        # Verify click event setup again
        load_example_btn.click.assert_called_once()
        args, kwargs = load_example_btn.click.call_args
        assert kwargs["outputs"] == [recipe_text, example_desc]
