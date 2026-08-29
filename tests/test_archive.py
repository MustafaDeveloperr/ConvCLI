"""Tests for zip and unzip commands."""

from __future__ import annotations

import zipfile
from pathlib import Path
from click.testing import CliRunner

from toolbox.cli import cli


class TestArchive:
    def test_zip_and_unzip(self, runner: CliRunner, tmp_path: Path) -> None:
        # Prepare source directory
        src_dir = tmp_path / "my_folder"
        src_dir.mkdir()
        (src_dir / "file1.txt").write_text("Hello 1")
        (src_dir / "file2.txt").write_text("Hello 2")

        zip_out = tmp_path / "archive.zip"
        res_zip = runner.invoke(cli, ["zip", str(src_dir), str(zip_out)])
        assert res_zip.exit_code == 0
        assert zip_out.exists()

        extract_dir = tmp_path / "extracted"
        res_unzip = runner.invoke(cli, ["unzip", str(zip_out), str(extract_dir)])
        assert res_unzip.exit_code == 0
        assert (extract_dir / "my_folder" / "file1.txt").read_text() == "Hello 1"
        assert (extract_dir / "my_folder" / "file2.txt").read_text() == "Hello 2"

    def test_unzip_missing_archive(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["unzip", "nonexistent.zip"])
        assert result.exit_code != 0
