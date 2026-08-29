"""Text utility commands.

All operations use Python stdlib — no external dependencies.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

import click

from toolbox.cli import cli
from toolbox.utils.output import console, print_error, print_result


@cli.group(name="text")
def text_group() -> None:
    """Text inspection and transformation utilities."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_file(path_str: str) -> str:
    path = Path(path_str)
    if not path.exists():
        print_error(f"File not found: {path_str}")
        sys.exit(1)
    if not path.is_file():
        print_error(f"Not a regular file: {path_str}")
        sys.exit(1)
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except PermissionError:
        print_error(f"Permission denied: {path_str}")
        sys.exit(1)


_CHAR_MAP = str.maketrans({
    "ı": "i", "İ": "i", "ş": "s", "Ş": "s",
    "ğ": "g", "Ğ": "g", "ü": "u", "Ü": "u",
    "ö": "o", "Ö": "o", "ç": "c", "Ç": "c",
})


def _slugify(text: str) -> str:
    """Convert *text* to a URL-safe slug.

    1. Map common non-ASCII Latin characters (e.g. Turkish ı, ş, ğ)
    2. Normalise Unicode (NFKD)
    3. Drop accents/diacritics
    4. Lowercase
    5. Replace non-alphanumeric characters with hyphens
    6. Collapse multiple hyphens, strip leading/trailing hyphens
    """
    text = text.translate(_CHAR_MAP)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@text_group.command(name="count")
@click.argument("file")
def text_count(file: str) -> None:
    """Show character, word, and line counts for FILE.

    \b
    Example:
      tool text count README.md
    """
    content = _read_file(file)
    lines = content.splitlines()
    words = content.split()
    chars = len(content)

    print_result("Lines ", str(len(lines)))
    print_result("Words ", str(len(words)))
    print_result("Chars ", str(chars))
    print_result("Bytes ", str(Path(file).stat().st_size))


@text_group.command(name="lines")
@click.argument("file")
def text_lines(file: str) -> None:
    """Count the number of lines in FILE.

    \b
    Example:
      tool text lines script.py
    """
    content = _read_file(file)
    console.print(str(len(content.splitlines())))


@text_group.command(name="words")
@click.argument("file")
def text_words(file: str) -> None:
    """Count the number of words in FILE.

    \b
    Example:
      tool text words essay.txt
    """
    content = _read_file(file)
    console.print(str(len(content.split())))


@text_group.command(name="upper")
@click.argument("text")
def text_upper(text: str) -> None:
    """Convert TEXT to UPPERCASE.

    \b
    Example:
      tool text upper "hello world"
    """
    console.print(text.upper())


@text_group.command(name="lower")
@click.argument("text")
def text_lower(text: str) -> None:
    """Convert TEXT to lowercase.

    \b
    Example:
      tool text lower "HELLO WORLD"
    """
    console.print(text.lower())


@text_group.command(name="slug")
@click.argument("text")
def text_slug(text: str) -> None:
    """Convert TEXT to a URL-safe slug.

    \b
    Examples:
      tool text slug "Hello World!"
      tool text slug "Ünlü Şarkıcı"
    """
    console.print(_slugify(text))
