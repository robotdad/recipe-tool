"""Tests for the app module."""

from unittest.mock import MagicMock, patch


class TestCreateApp:
    """Tests for create_app function."""

    @patch("recipe_tool_app.app.RecipeToolCore")
    @patch("recipe_tool_app.app.RecipeExecutorCore")
    @patch("recipe_tool_app.app.gr.Blocks")
    @patch("recipe_tool_app.app.gr.Markdown")
    @patch("recipe_tool_app.app.gr.Tabs")
    @patch("recipe_tool_app.app.gr.TabItem")
    @patch("recipe_tool_app.app.create_recipe_ui")
    @patch("recipe_tool_app.app.create_executor_block")
    def test_create_app(
        self,
        mock_executor_block,
        mock_recipe_ui,
        mock_tab_item,
        mock_tabs,
        mock_markdown,
        mock_blocks,
        mock_executor_core,
        mock_recipe_core,
    ):
        """Test create_app function."""
        # Setup context managers
        mock_app = MagicMock()
        mock_blocks.return_value.__enter__.return_value = mock_app
        mock_tabs.return_value.__enter__.return_value = MagicMock()
        mock_tab_item.return_value.__enter__.return_value = MagicMock()

        # Import and call
        from recipe_tool_app.app import create_app

        result = create_app()

        # Verify
        assert result == mock_app
        mock_recipe_core.assert_called_once()
        mock_executor_core.assert_called_once()
        mock_recipe_ui.assert_called_once()
        mock_executor_block.assert_called_once()


class TestMain:
    """Tests for main function."""

    @patch("recipe_tool_app.app.argparse.ArgumentParser")
    @patch("recipe_tool_app.app.create_app")
    @patch("recipe_tool_app.app.settings")
    def test_main_with_args(self, mock_settings, mock_create_app, mock_parser_class):
        """Test main function with command line arguments."""
        # Setup
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_args = MagicMock(host="127.0.0.1", port=8080, no_mcp=True, debug=True)
        mock_parser.parse_args.return_value = mock_args

        mock_app = MagicMock()
        mock_create_app.return_value = mock_app
        mock_settings.to_launch_kwargs.return_value = {}

        # Import and call main
        from recipe_tool_app.app import main

        main()

        # Verify settings were updated
        assert mock_settings.host == "127.0.0.1"
        assert mock_settings.port == 8080
        assert mock_settings.mcp_server is False
        assert mock_settings.debug is True

        # Verify app was launched
        mock_app.launch.assert_called_once()
