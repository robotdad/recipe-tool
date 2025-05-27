"""Tests for the app module."""

from unittest.mock import MagicMock, patch


from recipe_executor_app.app import get_components


class TestGetComponents:
    """Tests for get_components function."""

    def test_get_components_with_core(self):
        """Test get_components with provided core."""
        mock_core = MagicMock()
        mock_core.execute_recipe = MagicMock()
        mock_core.load_recipe = MagicMock()

        result = get_components(mock_core)

        assert "create_executor_block" in result
        assert "core" in result
        assert result["core"] == mock_core
        assert "execute_recipe" in result
        assert "load_recipe" in result

    @patch("recipe_executor_app.app.RecipeExecutorCore")
    def test_get_components_without_core(self, mock_core_class):
        """Test get_components without provided core."""
        mock_core = MagicMock()
        mock_core.execute_recipe = MagicMock()
        mock_core.load_recipe = MagicMock()
        mock_core_class.return_value = mock_core

        result = get_components()

        assert result["core"] == mock_core
        mock_core_class.assert_called_once()


class TestMain:
    """Tests for main function."""

    @patch("recipe_executor_app.app.argparse.ArgumentParser")
    @patch("recipe_executor_app.app.create_app")
    @patch("recipe_executor_app.app.settings")
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
        from recipe_executor_app.app import main

        main()

        # Verify settings were updated
        assert mock_settings.host == "127.0.0.1"
        assert mock_settings.port == 8080
        assert mock_settings.mcp_server is False
        assert mock_settings.debug is True

        # Verify app was launched
        mock_app.launch.assert_called_once()
