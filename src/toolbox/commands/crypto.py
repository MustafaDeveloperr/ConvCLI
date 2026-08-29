"""Crypto commands: hash, uuid, random.

hash    — streaming file/stdin hashing (never loads whole file into RAM)
uuid    — UUID v4 generation
random  — secure number, string, and password generation
"""

from __future__ import annotations

import hashlib
import secrets
import string
import sys
import uuid as _uuid_mod
from pathlib import Path

import click

from toolbox.cli import cli
from toolbox.utils.output import console, print_error, print_result


# ---------------------------------------------------------------------------
# Supported hash algorithms
# ---------------------------------------------------------------------------

_SUPPORTED_ALGOS = ("md5", "sha1", "sha256", "sha512", "sha3_256", "sha3_512")
_CHUNK_SIZE = 65536  # 64 KB chunks for streaming


def _hash_stream(algo: str, stream) -> str:  # type: ignore[type-arg]
    h = hashlib.new(algo)
    while True:
        chunk = stream.read(_CHUNK_SIZE)
        if not chunk:
            break
        if isinstance(chunk, str):
            chunk = chunk.encode()
        h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# hash command
# ---------------------------------------------------------------------------


@cli.command(name="hash")
@click.argument("algorithm", type=click.Choice(_SUPPORTED_ALGOS, case_sensitive=False))
@click.argument("file", default="-")
def hash_cmd(algorithm: str, file: str) -> None:
    """Compute the ALGORITHM hash of FILE (or stdin).

    \b
    Examples:
      tool hash sha256 file.txt
      tool hash md5 archive.zip
      echo "hello" | tool hash sha256
    """
    algo = algorithm.lower()

    if file == "-":
        # stdin — streaming
        stream = click.get_binary_stream("stdin")
        digest = _hash_stream(algo, stream)
        print_result(algo.upper(), digest)
        return

    path = Path(file)
    if not path.exists():
        print_error(f"File not found: {file}")
        sys.exit(1)
    if not path.is_file():
        print_error(f"Not a file: {file}")
        sys.exit(1)

    try:
        with path.open("rb") as fh:
            digest = _hash_stream(algo, fh)
    except PermissionError:
        print_error(f"Permission denied: {file}")
        sys.exit(1)

    print_result(algo.upper(), f"{digest}  {path.name}")


# ---------------------------------------------------------------------------
# uuid command
# ---------------------------------------------------------------------------


@cli.command(name="uuid")
@click.option("--count", "-n", default=1, show_default=True, help="Number of UUIDs to generate.")
def uuid_cmd(count: int) -> None:
    """Generate one or more random UUID v4 values.

    \b
    Examples:
      tool uuid
      tool uuid -n 5
    """
    for _ in range(count):
        console.print(str(_uuid_mod.uuid4()))


# ---------------------------------------------------------------------------
# random group
# ---------------------------------------------------------------------------


@cli.group(name="random")
def random_group() -> None:
    """Generate random numbers, strings, and passwords."""


@random_group.command(name="number")
@click.argument("min_val", type=int)
@click.argument("max_val", type=int)
def random_number(min_val: int, max_val: int) -> None:
    """Generate a random integer between MIN_VAL and MAX_VAL (inclusive).

    \b
    Example:
      tool random number 1 100
    """
    if min_val > max_val:
        print_error("MIN_VAL must be less than or equal to MAX_VAL.")
        sys.exit(1)
    # secrets.randbelow gives a uniform random int in [0, n)
    rng = secrets.randbelow(max_val - min_val + 1) + min_val
    console.print(str(rng))


@random_group.command(name="string")
@click.argument("length", type=int)
@click.option(
    "--charset",
    default="alphanumeric",
    type=click.Choice(["alphanumeric", "alpha", "digits", "hex"], case_sensitive=False),
    show_default=True,
    help="Character set to use.",
)
def random_string(length: int, charset: str) -> None:
    """Generate a random string of LENGTH characters.

    \b
    Example:
      tool random string 32
      tool random string 16 --charset hex
    """
    if length <= 0:
        print_error("Length must be a positive integer.")
        sys.exit(1)

    chars: str
    match charset.lower():
        case "alpha":
            chars = string.ascii_letters
        case "digits":
            chars = string.digits
        case "hex":
            chars = string.hexdigits[:16]  # 0-9, a-f
        case _:  # alphanumeric
            chars = string.ascii_letters + string.digits

    result = "".join(secrets.choice(chars) for _ in range(length))
    console.print(result)


@random_group.command(name="password")
@click.argument("length", type=int, default=24)
@click.option("--no-symbols", is_flag=True, help="Exclude special characters.")
def random_password(length: int, no_symbols: bool) -> None:
    """Generate a cryptographically secure random password.

    Uses Python's secrets module — suitable for real passwords.

    \b
    Examples:
      tool random password
      tool random password 32
      tool random password 16 --no-symbols
    """
    if length < 8:
        print_error("Password length must be at least 8 characters.")
        sys.exit(1)

    chars = string.ascii_letters + string.digits
    if not no_symbols:
        chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"

    # Guarantee at least one character from each required class
    required: list[str] = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
    ]
    if not no_symbols:
        required.append(secrets.choice("!@#$%^&*()-_=+[]{}|;:,.<>?"))

    remaining = [secrets.choice(chars) for _ in range(length - len(required))]
    password_chars = required + remaining
    # Shuffle using secrets-safe approach
    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

    console.print("".join(password_chars))
