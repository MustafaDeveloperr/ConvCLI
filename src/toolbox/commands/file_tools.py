"""File utility commands: file info, directory size.

Uses pathlib/stat — no external dependencies.
"""

from __future__ import annotations

import stat
import sys
from pathlib import Path

import click
from rich.table import Table

from toolbox.cli import cli
from toolbox.utils.files import directory_size, human_size
from toolbox.utils.output import console, print_error


@cli.group(name="file")
def file_group() -> None:
    """File inspection utilities."""


@file_group.command(name="info")
@click.argument("path")
def file_info(path: str) -> None:
    """Show detailed information about a file or directory.

    \b
    Example:
      tool file info image.png
      tool file info ./project/
    """
    p = Path(path)
    if not p.exists():
        print_error(f"Path not found: {path}")
        sys.exit(1)

    try:
        st = p.lstat()  # lstat to avoid following symlinks
    except PermissionError:
        print_error(f"Permission denied: {path}")
        sys.exit(1)

    is_symlink = p.is_symlink()
    if is_symlink:
        try:
            real = p.resolve()
            link_target = f" → {real}"
        except Exception:
            link_target = " → (unresolvable)"
    else:
        link_target = ""

    if stat.S_ISDIR(st.st_mode):
        kind = "Directory"
        size_bytes = directory_size(p)
    elif stat.S_ISLNK(st.st_mode):
        kind = "Symlink" + link_target
        size_bytes = st.st_size
    elif stat.S_ISREG(st.st_mode):
        kind = "Regular file"
        size_bytes = st.st_size
    else:
        kind = "Special file"
        size_bytes = st.st_size

    import datetime

    modified = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    perms = stat.filemode(st.st_mode)

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Key", style="bold cyan", no_wrap=True)
    table.add_column("Value")

    table.add_row("Name", p.name)
    table.add_row("Path", str(p.resolve()))
    table.add_row("Type", kind)
    table.add_row("Size", f"{human_size(size_bytes)}  ({size_bytes:,} bytes)")
    table.add_row("Modified", modified)
    table.add_row("Permissions", perms)

    console.print()
    console.print(table)
    console.print()


@file_group.command(name="size")
@click.argument("path")
@click.option("--human", "-H", is_flag=True, default=True, help="Show human-readable size.")
def file_size(path: str, human: bool) -> None:
    """Show total size of a file or directory.

    \b
    Examples:
      tool file size ./project
      tool file size video.mp4
    """
    p = Path(path)
    if not p.exists():
        print_error(f"Path not found: {path}")
        sys.exit(1)

    if p.is_dir():
        total = directory_size(p)
    else:
        try:
            total = p.stat().st_size
        except PermissionError:
            print_error(f"Permission denied: {path}")
            sys.exit(1)

    if human:
        console.print(f"{human_size(total)}  [dim]({total:,} bytes)[/dim]")
    else:
        console.print(str(total))
