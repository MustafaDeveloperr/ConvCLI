"""Tests for root CLI options, help, and version."""

from __future__ import annotations

from click.testing import CliRunner
from toolbox import __version__
from toolbox.cli import cli


def test_cli_help(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "TOOLBOX" in result.output
    assert "Media" in result.output
    assert "Convert" in result.output


def test_cli_help_alias(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["help"])
    assert result.exit_code == 0
    assert "TOOLBOX" in result.output


def test_cli_help_specific_command(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["help", "convert"])
    assert result.exit_code == 0
    assert "Convert VALUE from FROM_UNIT to TO_UNIT" in result.output


def test_cli_version(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output
