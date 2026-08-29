"""Encoding commands: base64 and URL encode/decode.

All encoding/decoding uses Python stdlib only (base64, urllib.parse).
"""

from __future__ import annotations

import base64
import sys
import urllib.parse
from pathlib import Path

import click

from toolbox.cli import cli
from toolbox.errors import AppError
from toolbox.utils.output import print_error, print_success, console


# ---------------------------------------------------------------------------
# base64 group
# ---------------------------------------------------------------------------


@cli.group(name="base64")
def base64_group() -> None:
    """Base64 encode or decode text and files."""


@base64_group.command(name="encode")
@click.argument("input", default="-")
@click.option("--file", "-f", is_flag=True, help="Treat INPUT as a file path.")
def base64_encode(input: str, file: bool) -> None:
    """Encode text or a file to base64.

    \b
    Examples:
      tool base64 encode "Hello World"
      tool base64 encode -f image.png
      echo "hello" | tool base64 encode
    """
    raw: bytes
    if file or (input != "-" and Path(input).exists()):
        path = Path(input)
        if not path.exists():
            print_error(f"File not found: {input}")
            sys.exit(1)
        raw = path.read_bytes()
    elif input == "-":
        raw = click.get_binary_stream("stdin").read()
    else:
        raw = input.encode("utf-8")

    encoded = base64.b64encode(raw).decode("ascii")
    console.print(encoded)


@base64_group.command(name="decode")
@click.argument("input", default="-")
@click.option("--file", "-f", is_flag=True, help="Treat INPUT as a file path.")
@click.option("--output", "-o", default=None, help="Write decoded bytes to this file.")
def base64_decode(input: str, file: bool, output: str | None) -> None:
    """Decode base64 text or a file.

    \b
    Examples:
      tool base64 decode "SGVsbG8gV29ybGQ="
      tool base64 decode -f encoded.txt
      echo "SGVsbG8=" | tool base64 decode
    """
    raw_b64: bytes
    if file or (input != "-" and Path(input).exists()):
        path = Path(input)
        if not path.exists():
            print_error(f"File not found: {input}")
            sys.exit(1)
        raw_b64 = path.read_bytes()
    elif input == "-":
        raw_b64 = click.get_binary_stream("stdin").read()
    else:
        raw_b64 = input.encode("ascii")

    try:
        decoded = base64.b64decode(raw_b64)
    except Exception as exc:
        print_error("Base64 decode failed.", reason=str(exc))
        sys.exit(1)

    if output:
        out_path = Path(output)
        out_path.write_bytes(decoded)
        print_success("Decoded successfully.", output_path=out_path)
    else:
        # Try to print as text; fall back to raw bytes notice.
        try:
            console.print(decoded.decode("utf-8"))
        except UnicodeDecodeError:
            sys.stdout.buffer.write(decoded)


# ---------------------------------------------------------------------------
# url group
# ---------------------------------------------------------------------------


@cli.group(name="url")
def url_group() -> None:
    """URL encode or decode text."""


@url_group.command(name="encode")
@click.argument("text")
def url_encode(text: str) -> None:
    """Percent-encode TEXT for use in a URL.

    \b
    Example:
      tool url encode "hello world & more"
    """
    encoded = urllib.parse.quote(text, safe="")
    console.print(encoded)


@url_group.command(name="decode")
@click.argument("text")
def url_decode(text: str) -> None:
    """Decode a percent-encoded URL string.

    \b
    Example:
      tool url decode "hello%20world%20%26%20more"
    """
    decoded = urllib.parse.unquote(text)
    console.print(decoded)
