"""FFmpeg service — wraps ffmpeg/ffprobe calls safely.

All subprocess calls use shell=False with a list of arguments.
"""

from __future__ import annotations

from pathlib import Path

from toolbox.errors import require_ffmpeg, require_ffprobe
from toolbox.utils.run import run


def run_ffmpeg(
    args: list[str | Path],
    *,
    verbose: bool = False,
    overwrite: bool = True,
) -> None:
    """Run ffmpeg with the given arguments.

    Args:
        args: Arguments to pass after `ffmpeg`.
        verbose: If True, show the ffmpeg command before running.
        overwrite: If True, prepend -y to overwrite output without prompt.
    """
    ffmpeg = require_ffmpeg()
    prefix: list[str | Path] = [ffmpeg]
    if not verbose:
        prefix += ["-loglevel", "error"]
    if overwrite:
        prefix.append("-y")
    run(prefix + args, verbose=verbose)


def probe_duration(input_path: Path) -> float | None:
    """Return the duration in seconds of a media file, or None on failure."""
    ffprobe = require_ffprobe()
    try:
        result = run(
            [
                ffprobe,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(input_path),
            ],
            capture_stdout=True,
        )
        return float(result.stdout.strip())
    except Exception:
        return None


def parse_time(time_str: str) -> float:
    """Parse a time string like MM:SS or HH:MM:SS into seconds.

    Raises:
        ValueError: If the format is not recognised.
    """
    parts = time_str.split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    elif len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    else:
        # Try plain seconds
        return float(time_str)
