"""Output formatting helpers for Toolbox CLI — pure Click/Stdlib output (Zero Rich dependency).
"""

from __future__ import annotations

import sys
from pathlib import Path
import click


class StandardConsole:
    """Lightweight console output wrapper."""

    def __init__(self, stderr: bool = False) -> None:
        self._stderr = stderr

    def print(self, *args: object, **kwargs: object) -> None:
        msg = " ".join(str(a) for a in args)
        click.echo(msg, err=self._stderr)

    def print_json(self, json_str: str) -> None:
        click.echo(json_str, err=self._stderr)


console = StandardConsole(stderr=False)
err_console = StandardConsole(stderr=True)


def print_success(
    message: str,
    *,
    input_path: Path | str | None = None,
    output_path: Path | str | None = None,
) -> None:
    """Print a ✓ success message with optional input/output paths."""
    click.echo(f"✓ {message}")
    if input_path is not None:
        click.echo(f"  Input :  {input_path}")
    if output_path is not None:
        click.echo(f"  Output:  {output_path}")


def print_error(message: str, *, reason: str | None = None, hint: str | None = None) -> None:
    """Print a ✗ error message to stderr with an optional reason and hint."""
    click.echo(f"✗ {message}", err=True)
    if reason:
        click.echo(f"\nReason:\n{reason}", err=True)
    if hint:
        click.echo(f"\nHint:\n{hint}", err=True)


def print_info(message: str) -> None:
    """Print an informational line."""
    click.echo(message)


def print_result(label: str, value: str) -> None:
    """Print a single key-value result line."""
    click.echo(f"{label}: {value}")


def print_verbose(message: str, *, verbose: bool) -> None:
    """Print a debug message only when verbose mode is active."""
    if verbose:
        click.echo(f"[verbose] {message}", err=True)
