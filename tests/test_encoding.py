"""Tests for base64 and URL encoding/decoding."""

from __future__ import annotations

import base64
from pathlib import Path
from click.testing import CliRunner

from toolbox.cli import cli


class TestBase64:
    def test_encode_string(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["base64", "encode", "Hello World"])
        assert result.exit_code == 0
        assert result.output.strip() == base64.b64encode(b"Hello World").decode("ascii")

    def test_decode_string(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["base64", "decode", "SGVsbG8gV29ybGQ="])
        assert result.exit_code == 0
        assert result.output.strip() == "Hello World"

    def test_encode_file(self, runner: CliRunner, tmp_path: Path) -> None:
        p = tmp_path / "test.txt"
        p.write_bytes(b"File content 123")
        result = runner.invoke(cli, ["base64", "encode", "-f", str(p)])
        assert result.exit_code == 0
        assert result.output.strip() == base64.b64encode(b"File content 123").decode("ascii")

    def test_decode_to_file(self, runner: CliRunner, tmp_path: Path) -> None:
        out_p = tmp_path / "out.bin"
        b64_str = base64.b64encode(b"Binary data").decode("ascii")
        result = runner.invoke(cli, ["base64", "decode", b64_str, "-o", str(out_p)])
        assert result.exit_code == 0
        assert out_p.read_bytes() == b"Binary data"

    def test_encode_stdin(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["base64", "encode"], input="Piped content")
        assert result.exit_code == 0
        assert result.output.strip() == base64.b64encode(b"Piped content").decode("ascii")

    def test_decode_invalid_b64(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["base64", "decode", "Invalid base64 string!!!"])
        assert result.exit_code != 0


class TestUrl:
    def test_url_encode(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["url", "encode", "hello world & foo=bar"])
        assert result.exit_code == 0
        assert result.output.strip() == "hello%20world%20%26%20foo%3Dbar"

    def test_url_decode(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["url", "decode", "hello%20world%20%26%20foo%3Dbar"])
        assert result.exit_code == 0
        assert result.output.strip() == "hello world & foo=bar"
