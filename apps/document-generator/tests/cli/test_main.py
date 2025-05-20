from typer.testing import CliRunner  # type: ignore
from document_generator.cli.main import app

runner = CliRunner()


def test_cli_no_args():
    result = runner.invoke(app, [])
    assert result.exit_code != 0
