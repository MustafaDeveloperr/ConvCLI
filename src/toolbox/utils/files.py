"""File and path utilities for Toolbox CLI."""

from __future__ import annotations

from pathlib import Path


def resolve_output_path(
    input_path: Path,
    suffix: str,
    output_dir: Path | None = None,
    stem_override: str | None = None,
) -> Path:
    """Build a sensible output path from an input path.

    Args:
        input_path: The source file.
        suffix: Target extension including the dot, e.g. ".mp4".
        output_dir: Directory to place the output file in.
                    Defaults to the input file's parent directory.
        stem_override: Use this stem instead of the input stem.

    Returns:
        A Path for the output file.  The path is not created.
    """
    stem = stem_override if stem_override is not None else input_path.stem
    directory = output_dir if output_dir is not None else input_path.parent
    return directory / f"{stem}{suffix}"


def ensure_dir(path: Path) -> Path:
    """Create *path* (and any parents) if it does not already exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def human_size(size_bytes: int) -> str:
    """Return a human-readable representation of *size_bytes*."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes //= 1024
    return f"{size_bytes:.1f} PB"


def directory_size(path: Path) -> int:
    """Recursively compute total byte count of all files under *path*.

    Symlinks are counted by their own size (lstat), not followed.
    Handles PermissionError gracefully by skipping inaccessible entries.
    """
    total = 0
    try:
        for entry in path.rglob("*"):
            try:
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat(follow_symlinks=False).st_size
            except (PermissionError, OSError):
                pass
    except (PermissionError, OSError):
        pass
    return total


def safe_output_path(path: Path) -> Path:
    """Return *path* unchanged, or a non-conflicting variant if it exists.

    Appends ``_1``, ``_2``, … to the stem until a free name is found.
    """
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1
