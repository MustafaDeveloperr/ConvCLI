"""Shared test fixtures and helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from toolbox.cli import cli


@pytest.fixture()
def runner() -> CliRunner:
    """Click test runner that mixes stdout/stderr."""
    return CliRunner()


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def sample_json(tmp_path: Path) -> Path:
    """A valid JSON file."""
    p = tmp_path / "data.json"
    p.write_text(json.dumps({"name": "Mustafa", "age": 30, "active": True}))
    return p


@pytest.fixture()
def empty_file(tmp_path: Path) -> Path:
    p = tmp_path / "empty.txt"
    p.touch()
    return p


@pytest.fixture()
def text_file(tmp_path: Path) -> Path:
    p = tmp_path / "hello.txt"
    p.write_text("Hello World\nThis is line two\nLine three\n", encoding="utf-8")
    return p


@pytest.fixture()
def unicode_file(tmp_path: Path) -> Path:
    p = tmp_path / "Ünlü_şarkıcı.txt"
    p.write_text("Merhaba Dünya\n", encoding="utf-8")
    return p
