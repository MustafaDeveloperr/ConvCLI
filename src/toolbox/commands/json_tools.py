"""JSON tools: pretty-print, minify, validate.

All three commands read from a file argument or from stdin.
"""

from __future__ import annotations

import json
import sys

import click

from toolbox.cli import cli
from toolbox.utils.output import print_error


# ---------------------------------------------------------------------------
# json group
# ---------------------------------------------------------------------------


@cli.group(name="json")
def json_group() -> None:
    """Inspect, format, and validate JSON data."""


def _read_json_input(file: click.File) -> str:  # type: ignore[type-arg]
    """Read all text from a Click file object (which may be stdin)."""
    return file.read()


@json_group.command(name="pretty")
@click.argument("file", type=click.File("r"), default="-")
@click.option("--indent", "-i", default=2, show_default=True, help="Indentation width.")
def json_pretty(file: click.File, indent: int) -> None:  # type: ignore[type-arg]
    """Pretty-print JSON from FILE or stdin.

    \b
    Examples:
      tool json pretty data.json
      cat data.json | tool json pretty
      echo '{"name":"Mustafa"}' | tool json pretty
    """
    raw = _read_json_input(file)
    if not raw.strip():
        print_error("Input is empty.")
        sys.exit(1)

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        print_error("Invalid JSON.", reason=str(exc))
        sys.exit(1)

    click.echo(json.dumps(parsed, indent=indent, ensure_ascii=False))


@json_group.command(name="minify")
@click.argument("file", type=click.File("r"), default="-")
def json_minify(file: click.File) -> None:  # type: ignore[type-arg]
    """Remove all whitespace from JSON (minify).

    \b
    Examples:
      tool json minify data.json
      cat data.json | tool json minify
    """
    raw = _read_json_input(file)
    if not raw.strip():
        print_error("Input is empty.")
        sys.exit(1)

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        print_error("Invalid JSON.", reason=str(exc))
        sys.exit(1)

    click.echo(json.dumps(parsed, separators=(",", ":"), ensure_ascii=False))


@json_group.command(name="validate")
@click.argument("file", type=click.File("r"), default="-")
def json_validate(file: click.File) -> None:  # type: ignore[type-arg]
    """Check whether FILE (or stdin) contains valid JSON.

    \b
    Examples:
      tool json validate data.json
      echo '{}' | tool json validate
    """
    raw = _read_json_input(file)
    if not raw.strip():
        print_error("Input is empty.")
        sys.exit(1)

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        click.echo(f"✗ Invalid JSON\n\n{exc}", err=True)
        sys.exit(1)

    # Summarise the top-level structure
    if isinstance(parsed, dict):
        summary = f"object with {len(parsed)} key(s)"
    elif isinstance(parsed, list):
        summary = f"array with {len(parsed)} item(s)"
    else:
        summary = type(parsed).__name__

    click.echo(f"✓ Valid JSON — {summary}")
