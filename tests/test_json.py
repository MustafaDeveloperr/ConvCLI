"""Tests for JSON commands (pretty, minify, validate)."""

from __future__ import annotations

import json
from pathlib import Path
from click.testing import CliRunner

from toolbox.cli import cli


class TestJson:
    def test_json_pretty_file(self, runner: CliRunner, sample_json: Path) -> None:
        result = runner.invoke(cli, ["json", "pretty", str(sample_json)])
        assert result.exit_code == 0
        assert '"name": "Mustafa"' in result.output

    def test_json_pretty_stdin(self, runner: CliRunner) -> None:
        raw_json = '{"a":1,"b":2}'
        result = runner.invoke(cli, ["json", "pretty"], input=raw_json)
        assert result.exit_code == 0
        assert '"a": 1' in result.output

    def test_json_minify_file(self, runner: CliRunner, sample_json: Path) -> None:
        result = runner.invoke(cli, ["json", "minify", str(sample_json)])
        assert result.exit_code == 0
        assert '{"name":"Mustafa","age":30,"active":true}' in result.output.strip()

    def test_json_validate_valid(self, runner: CliRunner, sample_json: Path) -> None:
        result = runner.invoke(cli, ["json", "validate", str(sample_json)])
        assert result.exit_code == 0
        assert "Valid JSON" in result.output

    def test_json_validate_invalid(self, runner: CliRunner, tmp_path: Path) -> None:
        p = tmp_path / "bad.json"
        p.write_text("{bad json}")
        result = runner.invoke(cli, ["json", "validate", str(p)])
        assert result.exit_code != 0

    def test_json_empty_input(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["json", "pretty"], input="")
        assert result.exit_code != 0
