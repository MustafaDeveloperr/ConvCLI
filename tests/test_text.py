"""Tests for text commands (count, lines, words, upper, lower, slug)."""

from __future__ import annotations

from pathlib import Path
from click.testing import CliRunner

from toolbox.cli import cli


class TestText:
    def test_text_count(self, runner: CliRunner, text_file: Path) -> None:
        result = runner.invoke(cli, ["text", "count", str(text_file)])
        assert result.exit_code == 0
        assert "Lines" in result.output
        assert "Words" in result.output

    def test_text_lines(self, runner: CliRunner, text_file: Path) -> None:
        result = runner.invoke(cli, ["text", "lines", str(text_file)])
        assert result.exit_code == 0
        assert result.output.strip() == "3"

    def test_text_words(self, runner: CliRunner, text_file: Path) -> None:
        result = runner.invoke(cli, ["text", "words", str(text_file)])
        assert result.exit_code == 0
        assert result.output.strip() == "8"

    def test_text_upper(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["text", "upper", "hello world"])
        assert result.exit_code == 0
        assert result.output.strip() == "HELLO WORLD"

    def test_text_lower(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["text", "lower", "HELLO WORLD"])
        assert result.exit_code == 0
        assert result.output.strip() == "hello world"

    def test_text_slug(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["text", "slug", "Hello World! Ünlü Şarkıcı"])
        assert result.exit_code == 0
        assert result.output.strip() == "hello-world-unlu-sarkici"
