"""Toolbox CLI — root command group and error handling middleware.

Entry point: `tool` (defined in pyproject.toml [project.scripts])
"""

from __future__ import annotations

import sys

import click

from toolbox import __version__
from toolbox.errors import AppError

# ---------------------------------------------------------------------------
# Context settings applied to every command
# ---------------------------------------------------------------------------

CONTEXT_SETTINGS = dict(
    help_option_names=["--help", "-h"],
    max_content_width=100,
)


# ---------------------------------------------------------------------------
# Root group
# ---------------------------------------------------------------------------


class ToolboxGroup(click.Group):
    """Custom group that catches AppError and prints a clean message."""

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        _print_categorised_help()

    def invoke(self, ctx: click.Context) -> object:
        try:
            return super().invoke(ctx)
        except AppError as exc:
            click.echo(f"\n✗ {exc.message}", err=True)
            if exc.hint:
                click.echo(f"\n{exc.hint}", err=True)
            sys.exit(1)


@click.group(
    cls=ToolboxGroup,
    context_settings=CONTEXT_SETTINGS,
    invoke_without_command=True,
)
@click.version_option(__version__, "--version", "-V", prog_name="conv")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Show detailed output and debug information.",
    envvar="TOOL_VERBOSE",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """CONV — a single command for daily Linux utility tasks.

    Run \b
        conv COMMAND --help

    for help on a specific command.
    """
    # Store verbose flag so subcommands can read it via ctx.obj
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    # If invoked with no subcommand, show the categorised help.
    if ctx.invoked_subcommand is None:
        _print_categorised_help()


# ---------------------------------------------------------------------------
# Built-in help alias
# ---------------------------------------------------------------------------


@cli.command(name="help", hidden=False)
@click.argument("command", required=False)
@click.pass_context
def help_cmd(ctx: click.Context, command: str | None) -> None:
    """Show help, optionally for a specific COMMAND."""
    if command is None:
        _print_categorised_help()
    else:
        # Delegate to the target command's --help.
        target = cli.get_command(ctx, command)
        if target is None:
            click.echo(f"✗ Unknown command: {command}", err=True)
            sys.exit(1)
        with click.Context(target, info_name=f"conv {command}") as sub_ctx:
            click.echo(target.get_help(sub_ctx))


# ---------------------------------------------------------------------------
# Categorised help renderer
# ---------------------------------------------------------------------------

_CATEGORIES: list[tuple[str, list[str]]] = [
    (
        "Media",
        [
            "gif-to-png",
            "gif-to-jpg",
            "gif-to-webp",
            "image-convert",
            "image-resize",
            "image-compress",
            "image-crop",
        ],
    ),
    (
        "Video / Audio",
        [
            "media-convert",
            "mp3-to-mp4",
            "mp4-to-mp3",
            "mp4-to-wav",
            "mp4-to-gif",
            "mp4-to-webm",
            "video-trim",
            "video-resize",
            "video-compress",
        ],
    ),
    (
        "Convert",
        ["convert"],
    ),
    (
        "Data / SQL",
        [
            "json",
            "base64",
            "url",
            "sql-to-json",
            "json-to-sql",
            "csv-to-json",
            "json-to-csv",
            "xml-to-json",
        ],
    ),
    (
        "Crypto",
        ["hash", "uuid", "random"],
    ),
    (
        "File",
        ["file", "zip", "unzip"],
    ),
    (
        "Text",
        ["text"],
    ),
]


def _print_categorised_help() -> None:
    lines = []
    lines.append("")
    lines.append(f"  CONV  v{__version__}")
    lines.append("  A single command for daily Linux utility tasks.")
    lines.append("")

    for category, commands in _CATEGORIES:
        lines.append(f"  {category:<15} {" ".join(commands)}")

    lines.append("")
    lines.append("  Usage:  conv COMMAND [ARGS]...")
    lines.append("          conv COMMAND --help  for command-specific help")
    lines.append("          conv --version       show version and exit")
    lines.append("")

    click.echo("\n".join(lines))


# ---------------------------------------------------------------------------
# Register subcommands (imported lazily to keep startup fast)
# ---------------------------------------------------------------------------


def _register_commands() -> None:
    from toolbox.commands import convert   # noqa: F401
    from toolbox.commands import encoding  # noqa: F401
    from toolbox.commands import crypto    # noqa: F401
    from toolbox.commands import json_tools  # noqa: F401
    from toolbox.commands import data_tools  # noqa: F401
    from toolbox.commands import text      # noqa: F401
    from toolbox.commands import file_tools  # noqa: F401
    from toolbox.commands import archive   # noqa: F401
    from toolbox.commands import media     # noqa: F401
    from toolbox.commands import video     # noqa: F401


_register_commands()
