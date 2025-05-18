import pytest

from typer.testing import CliRunner
from document_generator.cli.main import app

runner = CliRunner()

def test_cli_no_args():
    result = runner.invoke(app, [])
    assert result.exit_code != 0