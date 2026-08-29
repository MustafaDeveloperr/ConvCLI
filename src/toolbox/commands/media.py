"""Image and GIF commands.

Requires Pillow. DependencyError is shown if not installed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from toolbox.cli import cli
from toolbox.errors import AppError
from toolbox.utils.files import ensure_dir, resolve_output_path
from toolbox.utils.output import print_error, print_info, print_success


_IMAGE_FORMATS = ("png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif")


def _parse_dimensions(dim_str: str) -> tuple[int, int]:
    """Parse a 'WxH' string into (width, height) integers."""
    try:
        parts = dim_str.lower().replace("×", "x").split("x")
        if len(parts) != 2:
            raise ValueError
        w, h = int(parts[0]), int(parts[1])
        if w <= 0 or h <= 0:
            raise ValueError
        return w, h
    except (ValueError, TypeError):
        raise AppError(
            f"Invalid dimensions: '{dim_str}'",
            hint="Use the format WxH, e.g. 1920x1080",
        )


def _require_image_file(path_str: str) -> Path:
    path = Path(path_str)
    if not path.exists():
        raise AppError(f"File not found: {path_str}")
    if not path.is_file():
        raise AppError(f"Not a regular file: {path_str}")
    return path


# ---------------------------------------------------------------------------
# image-convert
# ---------------------------------------------------------------------------


@cli.command(name="image-convert")
@click.argument("input_file")
@click.argument("target_format", type=click.Choice(_IMAGE_FORMATS, case_sensitive=False))
@click.option("--output", "-o", default=None, help="Output file path.")
@click.option("--quality", "-q", default=85, show_default=True, help="Quality 1-95 (JPEG/WEBP).")
def image_convert(input_file: str, target_format: str, output: str | None, quality: int) -> None:
    """Convert an image to a different format.

    \b
    Examples:
      tool image-convert photo.png jpg
      tool image-convert photo.jpg webp
      tool image-convert image.webp png
    """
    from toolbox.services.images import convert_image

    try:
        src = _require_image_file(input_file)
    except AppError as exc:
        print_error(exc.message)
        sys.exit(1)

    fmt = target_format.lower().rstrip("e") if target_format.lower() == "jpeg" else target_format.lower()
    suffix = ".jpg" if target_format.lower() in ("jpg", "jpeg") else f".{target_format.lower()}"
    out = Path(output) if output else resolve_output_path(src, suffix)

    try:
        convert_image(src, out, quality=quality)
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)
    except Exception as exc:
        print_error("Image conversion failed.", reason=str(exc))
        sys.exit(1)

    print_success("Converted successfully.", input_path=src, output_path=out)


# ---------------------------------------------------------------------------
# image-resize
# ---------------------------------------------------------------------------


@cli.command(name="image-resize")
@click.argument("input_file")
@click.argument("dimensions")
@click.option("--output", "-o", default=None, help="Output file path.")
def image_resize(input_file: str, dimensions: str, output: str | None) -> None:
    """Resize IMAGE to DIMENSIONS (WxH).

    \b
    Example:
      tool image-resize photo.png 1920x1080
    """
    from toolbox.services.images import resize_image

    try:
        src = _require_image_file(input_file)
        w, h = _parse_dimensions(dimensions)
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)

    out = Path(output) if output else resolve_output_path(src, src.suffix, stem_override=f"{src.stem}_{w}x{h}")

    try:
        resize_image(src, out, w, h)
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)
    except Exception as exc:
        print_error("Resize failed.", reason=str(exc))
        sys.exit(1)

    print_success(f"Resized to {w}×{h}.", input_path=src, output_path=out)


# ---------------------------------------------------------------------------
# image-compress
# ---------------------------------------------------------------------------


@cli.command(name="image-compress")
@click.argument("input_file")
@click.option("--quality", "-q", default=75, show_default=True, help="Quality 1-95 (JPEG/WEBP).")
@click.option("--output", "-o", default=None, help="Output file path.")
def image_compress(input_file: str, quality: int, output: str | None) -> None:
    """Compress an image by reducing quality.

    \b
    Example:
      tool image-compress photo.jpg --quality 60
    """
    from toolbox.services.images import compress_image

    try:
        src = _require_image_file(input_file)
    except AppError as exc:
        print_error(exc.message)
        sys.exit(1)

    out = Path(output) if output else resolve_output_path(
        src, src.suffix, stem_override=f"{src.stem}_compressed"
    )

    orig_size = src.stat().st_size

    try:
        compress_image(src, out, quality=quality)
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)
    except Exception as exc:
        print_error("Compression failed.", reason=str(exc))
        sys.exit(1)

    new_size = out.stat().st_size
    ratio = (1 - new_size / orig_size) * 100 if orig_size else 0
    print_success(
        f"Compressed ({ratio:.1f}% smaller).",
        input_path=src,
        output_path=out,
    )


# ---------------------------------------------------------------------------
# image-crop
# ---------------------------------------------------------------------------


@cli.command(name="image-crop")
@click.argument("input_file")
@click.argument("dimensions")
@click.option("--output", "-o", default=None, help="Output file path.")
def image_crop(input_file: str, dimensions: str, output: str | None) -> None:
    """Center-crop IMAGE to DIMENSIONS (WxH).

    \b
    Example:
      tool image-crop photo.png 800x600
    """
    from toolbox.services.images import crop_image

    try:
        src = _require_image_file(input_file)
        w, h = _parse_dimensions(dimensions)
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)

    out = Path(output) if output else resolve_output_path(
        src, src.suffix, stem_override=f"{src.stem}_cropped_{w}x{h}"
    )

    try:
        crop_image(src, out, w, h)
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)
    except Exception as exc:
        print_error("Crop failed.", reason=str(exc))
        sys.exit(1)

    print_success(f"Cropped to {w}×{h}.", input_path=src, output_path=out)


# ---------------------------------------------------------------------------
# gif-to-* commands
# ---------------------------------------------------------------------------


def _gif_export(
    gif_path_str: str,
    target_ext: str,
    output_dir_str: str | None,
    quality: int,
    format_label: str,
) -> None:
    from toolbox.services.images import gif_frames

    try:
        gif_path = _require_image_file(gif_path_str)
    except AppError as exc:
        print_error(exc.message)
        sys.exit(1)

    out_dir = Path(output_dir_str) if output_dir_str else gif_path.parent
    ensure_dir(out_dir)

    try:
        frames = gif_frames(gif_path)
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)
    except Exception as exc:
        print_error("Failed to read GIF.", reason=str(exc))
        sys.exit(1)

    if not frames:
        print_error("GIF contains no frames.")
        sys.exit(1)

    print_info(f"Extracting {len(frames)} frame(s) from {gif_path.name}…")

    output_paths = []
    for idx, frame in frames:
        frame_name = f"{gif_path.stem}_{idx + 1:04d}{target_ext}"
        out_path = out_dir / frame_name

        try:
            if target_ext in (".jpg", ".jpeg"):
                bg_module = frame._new(frame.im)  # noqa: SLF001
                from PIL import Image as _PILImage  # type: ignore[import-untyped]
                bg = _PILImage.new("RGB", frame.size, (255, 255, 255))
                bg.paste(frame, mask=frame.split()[-1])
                bg.save(out_path, quality=quality, optimize=True)
            elif target_ext == ".webp":
                frame.save(out_path, format="WEBP", quality=quality)
            else:  # .png
                frame.save(out_path, format="PNG", optimize=True)
        except Exception as exc:
            print_error(f"Failed to save frame {idx + 1}.", reason=str(exc))
            sys.exit(1)

        output_paths.append(out_path)

    print_success(
        f"Exported {len(output_paths)} {format_label} frame(s).",
        input_path=gif_path,
        output_path=out_dir,
    )


@cli.command(name="gif-to-png")
@click.argument("gif_file")
@click.option("--output-dir", "-d", default=None, help="Directory for output frames.")
def gif_to_png(gif_file: str, output_dir: str | None) -> None:
    """Extract GIF frames as PNG images.

    \b
    Example:
      tool gif-to-png animation.gif
      tool gif-to-png animation.gif --output-dir ./frames/
    """
    _gif_export(gif_file, ".png", output_dir, 85, "PNG")


@cli.command(name="gif-to-jpg")
@click.argument("gif_file")
@click.option("--output-dir", "-d", default=None, help="Directory for output frames.")
@click.option("--quality", "-q", default=85, show_default=True, help="JPEG quality.")
def gif_to_jpg(gif_file: str, output_dir: str | None, quality: int) -> None:
    """Extract GIF frames as JPEG images.

    \b
    Example:
      tool gif-to-jpg animation.gif
    """
    _gif_export(gif_file, ".jpg", output_dir, quality, "JPEG")


@cli.command(name="gif-to-webp")
@click.argument("gif_file")
@click.option("--output-dir", "-d", default=None, help="Directory for output frames.")
@click.option("--quality", "-q", default=85, show_default=True, help="WebP quality.")
def gif_to_webp(gif_file: str, output_dir: str | None, quality: int) -> None:
    """Extract GIF frames as WebP images.

    \b
    Example:
      tool gif-to-webp animation.gif
    """
    _gif_export(gif_file, ".webp", output_dir, quality, "WebP")
