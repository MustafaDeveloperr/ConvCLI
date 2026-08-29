"""Output formatting helpers for Toolbox CLI.

All user-facing output goes through these functions so that the style
remains consistent and can be toggled (e.g. --verbose, --quiet) in one
place.
"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Shared consoles — stdout for normal output, stderr for diagnostics.
console = Console()
err_console = Console(stderr=True)

# ---------------------------------------------------------------------------
# Success / error / info helpers
# ---------------------------------------------------------------------------


def print_success(
    message: str,
    *,
    input_path: Path | str | None = None,
    output_path: Path | str | None = None,
) -> None:
    """Print a green ✓ success message with optional input/output paths."""
    console.print(f"[bold green]✓[/bold green] {message}")
    if input_path is not None:
        console.print(f"  [dim]Input :[/dim]  {input_path}")
    if output_path is not None:
        console.print(f"  [dim]Output:[/dim]  {output_path}")


def print_error(message: str, *, reason: str | None = None, hint: str | None = None) -> None:
    """Print a red ✗ error message to stderr with an optional reason and hint."""
    err_console.print(f"[bold red]✗[/bold red] {message}")
    if reason:
        err_console.print(f"\n[dim]Reason:[/dim]\n{reason}")
    if hint:
        err_console.print(f"\n[dim]Hint:[/dim]\n{hint}")


def print_info(message: str) -> None:
    """Print a dim informational line (progress, etc.)."""
    console.print(f"[dim]{message}[/dim]")


def print_result(label: str, value: str) -> None:
    """Print a single key-value result line."""
    console.print(f"[bold cyan]{label}:[/bold cyan] {value}")


def print_verbose(message: str, *, verbose: bool) -> None:
    """Print a debug message only when verbose mode is active."""
    if verbose:
        err_console.print(f"[dim yellow][verbose][/dim yellow] {message}")
