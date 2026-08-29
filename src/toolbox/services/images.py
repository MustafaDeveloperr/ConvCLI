"""Pillow image-processing service.

Import-guarded: if Pillow is not installed, DependencyError is raised on first use.
"""

from __future__ import annotations

from pathlib import Path

from toolbox.errors import require_pillow


def _get_pil():  # type: ignore[return]
    """Return the PIL.Image module, raising DependencyError if unavailable."""
    require_pillow()
    from PIL import Image  # type: ignore[import-untyped]
    return Image


def gif_frames(gif_path: Path) -> list:  # type: ignore[type-arg]
    """Return a list of (frame_index, PIL.Image) tuples from an animated GIF."""
    Image = _get_pil()
    frames = []
    with Image.open(gif_path) as img:
        idx = 0
        try:
            while True:
                # Copy each frame in RGBA to preserve transparency
                frame = img.copy().convert("RGBA")
                frames.append((idx, frame))
                idx += 1
                img.seek(img.tell() + 1)
        except EOFError:
            pass
    return frames


def convert_image(
    input_path: Path,
    output_path: Path,
    *,
    quality: int = 85,
) -> None:
    """Convert an image to the format implied by output_path's extension.

    JPEG outputs are flattened (no alpha channel) with the given quality.
    """
    Image = _get_pil()
    with Image.open(input_path) as img:
        ext = output_path.suffix.lower().lstrip(".")
        if ext in ("jpg", "jpeg"):
            if img.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = bg
            img.save(output_path, format="JPEG", quality=quality, optimize=True)
        elif ext == "webp":
            img.save(output_path, format="WEBP", quality=quality)
        elif ext == "png":
            img.save(output_path, format="PNG", optimize=True)
        else:
            img.save(output_path)


def resize_image(input_path: Path, output_path: Path, width: int, height: int) -> None:
    """Resize an image to exactly width × height (no aspect ratio preservation)."""
    Image = _get_pil()
    with Image.open(input_path) as img:
        resized = img.resize((width, height), Image.LANCZOS)
        resized.save(output_path)


def crop_image(input_path: Path, output_path: Path, width: int, height: int) -> None:
    """Crop an image to width × height from the center."""
    Image = _get_pil()
    with Image.open(input_path) as img:
        iw, ih = img.size
        left = max((iw - width) // 2, 0)
        top = max((ih - height) // 2, 0)
        right = min(left + width, iw)
        bottom = min(top + height, ih)
        cropped = img.crop((left, top, right, bottom))
        cropped.save(output_path)


def compress_image(input_path: Path, output_path: Path, quality: int = 75) -> None:
    """Re-save an image with reduced quality (lossy for JPEG/WEBP)."""
    Image = _get_pil()
    ext = output_path.suffix.lower().lstrip(".")
    with Image.open(input_path) as img:
        if ext in ("jpg", "jpeg"):
            if img.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = bg
            img.save(output_path, format="JPEG", quality=quality, optimize=True)
        elif ext == "webp":
            img.save(output_path, format="WEBP", quality=quality)
        elif ext == "png":
            img.save(output_path, format="PNG", optimize=True)
        else:
            img.save(output_path, quality=quality)
