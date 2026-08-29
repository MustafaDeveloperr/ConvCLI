"""Tests for hash, uuid, and random commands."""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from click.testing import CliRunner

from toolbox.cli import cli


class TestHash:
    def test_hash_file_sha256(self, runner: CliRunner, tmp_path: Path) -> None:
        p = tmp_path / "file.txt"
        content = b"Hello Hash Test"
        p.write_bytes(content)
        expected = hashlib.sha256(content).hexdigest()

        result = runner.invoke(cli, ["hash", "sha256", str(p)])
        assert result.exit_code == 0
        assert expected in result.output

    def test_hash_stdin_md5(self, runner: CliRunner) -> None:
        content = b"stdin data"
        expected = hashlib.md5(content).hexdigest()

        result = runner.invoke(cli, ["hash", "md5"], input=content)
        assert result.exit_code == 0
        assert expected in result.output

    def test_hash_missing_file(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["hash", "sha256", "nonexistent_file_xyz.txt"])
        assert result.exit_code != 0


class TestUuid:
    def test_uuid_generation(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["uuid"])
        assert result.exit_code == 0
        val = result.output.strip()
        parsed = uuid.UUID(val, version=4)
        assert str(parsed) == val

    def test_uuid_multiple(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["uuid", "-n", "3"])
        assert result.exit_code == 0
        lines = result.output.strip().splitlines()
        assert len(lines) == 3
        for line in lines:
            uuid.UUID(line, version=4)


class TestRandom:
    def test_random_number(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["random", "number", "10", "20"])
        assert result.exit_code == 0
        val = int(result.output.strip())
        assert 10 <= val <= 20

    def test_random_number_invalid_range(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["random", "number", "50", "20"])
        assert result.exit_code != 0

    def test_random_string(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["random", "string", "16"])
        assert result.exit_code == 0
        val = result.output.strip()
        assert len(val) == 16

    def test_random_password(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["random", "password", "24"])
        assert result.exit_code == 0
        pwd = result.output.strip()
        assert len(pwd) == 24
