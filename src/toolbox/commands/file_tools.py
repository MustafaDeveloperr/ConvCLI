"""File utility commands: file info, directory size.

Uses pathlib/stat — no external dependencies.
"""

from __future__ import annotations

import datetime
import stat
import sys
from pathlib import Path

import click

from toolbox.cli import cli
from toolbox.utils.files import directory_size, human_size
from toolbox.utils.output import print_error


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

    modified = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    perms = stat.filemode(st.st_mode)

    lines = [
        "",
        f"  Name        : {p.name}",
        f"  Path        : {p.resolve()}",
        f"  Type        : {kind}",
        f"  Size        : {human_size(size_bytes)} ({size_bytes:,} bytes)",
        f"  Modified    : {modified}",
        f"  Permissions : {perms}",
        "",
    ]
    click.echo("\n".join(lines))


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
        click.echo(f"{human_size(total)} ({total:,} bytes)")
    else:
        click.echo(str(total))
