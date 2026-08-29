"""Tests for file info and size commands."""

from __future__ import annotations

from pathlib import Path
from click.testing import CliRunner

from toolbox.cli import cli


class TestFileTools:
    def test_file_info(self, runner: CliRunner, text_file: Path) -> None:
        result = runner.invoke(cli, ["file", "info", str(text_file)])
        assert result.exit_code == 0
        assert "Name" in result.output
        assert text_file.name in result.output

    def test_file_size(self, runner: CliRunner, text_file: Path) -> None:
        result = runner.invoke(cli, ["file", "size", str(text_file)])
        assert result.exit_code == 0
        assert "B" in result.output

    def test_file_info_missing(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["file", "info", "missing_file_xyz.txt"])
        assert result.exit_code != 0
