"""Archive commands: zip and unzip.

Uses Python stdlib zipfile — no external dependencies.
Security: Path traversal attacks are blocked during extraction.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import click

from toolbox.cli import cli
from toolbox.utils.files import ensure_dir, human_size
from toolbox.utils.output import console, print_error, print_info, print_success


@cli.command(name="zip")
@click.argument("source")
@click.argument("output", required=False)
@click.option("--verbose", "-v", is_flag=True, help="List files as they are added.")
def zip_cmd(source: str, output: str | None, verbose: bool) -> None:
    """Create a ZIP archive from SOURCE (file or directory).

    \b
    Examples:
      tool zip folder/
      tool zip folder/ backup.zip
      tool zip report.pdf report.zip
    """
    src = Path(source)
    if not src.exists():
        print_error(f"Source not found: {source}")
        sys.exit(1)

    # Determine output path
    if output is None:
        out = src.with_suffix(".zip") if src.is_file() else src.parent / f"{src.name}.zip"
    else:
        out = Path(output)
        if not out.suffix:
            out = out.with_suffix(".zip")

    if out.exists():
        print_error(f"Output already exists: {out}")
        sys.exit(1)

    try:
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            if src.is_file():
                zf.write(src, src.name)
                if verbose:
                    print_info(f"  adding: {src.name}")
            else:
                for file in sorted(src.rglob("*")):
                    if file.is_file():
                        arc_name = file.relative_to(src.parent)
                        zf.write(file, arc_name)
                        if verbose:
                            print_info(f"  adding: {arc_name}")
    except PermissionError as exc:
        print_error("Permission denied.", reason=str(exc))
        sys.exit(1)

    size = out.stat().st_size
    print_success(
        f"Archive created  ({human_size(size)})",
        input_path=src,
        output_path=out,
    )


@cli.command(name="unzip")
@click.argument("archive")
@click.argument("output_dir", required=False)
@click.option("--verbose", "-v", is_flag=True, help="List files as they are extracted.")
def unzip_cmd(archive: str, output_dir: str | None, verbose: bool) -> None:
    """Extract a ZIP archive.

    \b
    Examples:
      tool unzip archive.zip
      tool unzip archive.zip ./extracted/
    """
    arc = Path(archive)
    if not arc.exists():
        print_error(f"Archive not found: {archive}")
        sys.exit(1)
    if not arc.suffix.lower() == ".zip":
        print_error(f"Not a .zip file: {archive}")
        sys.exit(1)
    if not zipfile.is_zipfile(arc):
        print_error(f"File is not a valid ZIP archive: {archive}")
        sys.exit(1)

    dest = Path(output_dir) if output_dir else arc.parent / arc.stem
    ensure_dir(dest)

    try:
        with zipfile.ZipFile(arc, "r") as zf:
            for member in zf.infolist():
                # --- Security: block path traversal ---
                member_path = dest / member.filename
                try:
                    member_path.resolve().relative_to(dest.resolve())
                except ValueError:
                    print_error(
                        "Path traversal detected — extraction aborted.",
                        reason=f"Malicious entry: {member.filename}",
                    )
                    sys.exit(1)

                if verbose:
                    print_info(f"  extracting: {member.filename}")
                zf.extract(member, dest)
    except PermissionError as exc:
        print_error("Permission denied.", reason=str(exc))
        sys.exit(1)
    except zipfile.BadZipFile as exc:
        print_error("Corrupt ZIP archive.", reason=str(exc))
        sys.exit(1)

    print_success("Extracted successfully.", input_path=arc, output_path=dest)
