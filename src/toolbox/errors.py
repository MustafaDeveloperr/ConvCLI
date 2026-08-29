"""Centralized error types and dependency-check helpers for Toolbox CLI."""

from __future__ import annotations

import shutil
import sys
from typing import Sequence


class AppError(Exception):
    """Raised for known, user-facing errors.

    Catching this in the CLI layer will display a clean error message
    without a Python traceback.
    """

    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint


class DependencyError(AppError):
    """Raised when a required external tool or library is missing."""


# ---------------------------------------------------------------------------
# Dependency check helpers
# ---------------------------------------------------------------------------

_FFMPEG_INSTALL_HINT = """\
Install FFmpeg for your distribution:

  Fedora / RHEL:
    sudo dnf install ffmpeg

  Debian / Ubuntu:
    sudo apt install ffmpeg

  Arch Linux:
    sudo pacman -S ffmpeg

  openSUSE:
    sudo zypper install ffmpeg"""


def require_ffmpeg() -> str:
    """Return the path to the ffmpeg binary or raise DependencyError."""
    binary = shutil.which("ffmpeg")
    if binary is None:
        raise DependencyError(
            "FFmpeg is not installed.",
            hint=_FFMPEG_INSTALL_HINT,
        )
    return binary


def require_ffprobe() -> str:
    """Return the path to the ffprobe binary or raise DependencyError."""
    binary = shutil.which("ffprobe")
    if binary is None:
        raise DependencyError(
            "ffprobe is not installed (it is usually bundled with FFmpeg).",
            hint=_FFMPEG_INSTALL_HINT,
        )
    return binary


def require_pillow() -> None:
    """Import Pillow or raise DependencyError with install instructions."""
    try:
        import PIL  # noqa: F401
    except ImportError:
        raise DependencyError(
            "Pillow is not installed.",
            hint=(
                "Install it with:\n\n"
                "  pip install Pillow\n\n"
                "Or install toolbox with image support:\n\n"
                "  pip install 'toolbox-cli[images]'"
            ),
        )
