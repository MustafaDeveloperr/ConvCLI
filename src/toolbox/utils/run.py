"""Safe subprocess wrapper for Toolbox CLI.

Rules enforced here:
- shell=True is NEVER used.
- Arguments are always passed as a list (no injection via user input).
- stderr is captured and converted to a clean AppError on failure.
- Exit codes are checked explicitly.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from toolbox.errors import AppError


def run(
    args: list[str | Path],
    *,
    verbose: bool = False,
    capture_stdout: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run an external command safely.

    Args:
        args: Command + arguments as a list.  Paths are converted to strings.
        verbose: If True, print the command being run before executing.
        capture_stdout: If True, capture stdout and return it in the result.

    Returns:
        The completed process object.

    Raises:
        AppError: If the process exits with a non-zero status.
    """
    str_args = [str(a) for a in args]

    if verbose:
        from toolbox.utils.output import print_verbose
        print_verbose(" ".join(str_args), verbose=True)

    try:
        result = subprocess.run(
            str_args,
            shell=False,
            check=False,
            text=True,
            capture_output=True,
        )
    except FileNotFoundError:
        raise AppError(
            f"Command not found: {str_args[0]}",
            hint=f"Make sure '{str_args[0]}' is installed and available in PATH.",
        )

    if result.returncode != 0:
        stderr_text = result.stderr.strip() if result.stderr else "(no error output)"
        raise AppError(
            f"Command failed: {str_args[0]}",
            reason=stderr_text,
        )

    return result
