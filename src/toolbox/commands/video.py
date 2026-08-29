"""Video and audio commands — all backed by FFmpeg.

Commands:
    mp3-to-mp4      convert MP3 to MP4 (with optional cover image)
    mp4-to-mp3      extract audio as MP3
    mp4-to-wav      extract audio as WAV
    mp4-to-gif      convert video to animated GIF
    mp4-to-webm     convert video to WebM
    video-trim      trim a video to a time range
    video-resize    resize a video to given dimensions
    video-compress  compress a video (H.264, CRF 28)
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from toolbox.cli import cli
from toolbox.errors import AppError
from toolbox.services.ffmpeg import parse_time, run_ffmpeg
from toolbox.utils.files import resolve_output_path
from toolbox.utils.output import print_error, print_info, print_success


def _require_video(path_str: str, label: str = "Video") -> Path:
    path = Path(path_str)
    if not path.exists():
        raise AppError(f"{label} file not found: {path_str}")
    if not path.is_file():
        raise AppError(f"Not a regular file: {path_str}")
    return path


def _parse_dims(dim_str: str) -> tuple[int, int]:
    try:
        parts = dim_str.lower().replace("×", "x").split("x")
        w, h = int(parts[0]), int(parts[1])
        if w <= 0 or h <= 0:
            raise ValueError
        return w, h
    except Exception:
        raise AppError(
            f"Invalid dimensions: '{dim_str}'",
            hint="Use WxH format, e.g. 1920x1080",
        )


# ---------------------------------------------------------------------------
# mp3-to-mp4
# ---------------------------------------------------------------------------


@cli.command(name="mp3-to-mp4")
@click.argument("mp3_file")
@click.argument("cover_image", required=False)
@click.option("--output", "-o", default=None, help="Output MP4 file path.")
@click.pass_context
def mp3_to_mp4(ctx: click.Context, mp3_file: str, cover_image: str | None, output: str | None) -> None:
    """Convert an MP3 file to MP4 video (with optional cover image).

    Without a cover, a black background is used.

    \b
    Examples:
      tool mp3-to-mp4 song.mp3
      tool mp3-to-mp4 song.mp3 cover.jpg
      tool mp3-to-mp4 song.mp3 cover.jpg --output song.mp4
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    try:
        src = _require_video(mp3_file, "MP3")
    except AppError as exc:
        print_error(exc.message)
        sys.exit(1)

    out = Path(output) if output else resolve_output_path(src, ".mp4")

    try:
        if cover_image:
            cov = Path(cover_image)
            if not cov.exists():
                print_error(f"Cover image not found: {cover_image}")
                sys.exit(1)
            print_info("Converting MP3 → MP4 with cover image…")
            run_ffmpeg(
                [
                    "-loop", "1",
                    "-i", str(cov),
                    "-i", str(src),
                    "-c:v", "libx264",
                    "-tune", "stillimage",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-pix_fmt", "yuv420p",
                    "-shortest",
                    str(out),
                ],
                verbose=verbose,
            )
        else:
            print_info("Converting MP3 → MP4 (black background)…")
            run_ffmpeg(
                [
                    "-f", "lavfi",
                    "-i", "color=c=black:s=1280x720:r=1",
                    "-i", str(src),
                    "-c:v", "libx264",
                    "-tune", "stillimage",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-pix_fmt", "yuv420p",
                    "-shortest",
                    str(out),
                ],
                verbose=verbose,
            )
    except AppError as exc:
        print_error(exc.message, reason=exc.hint)
        sys.exit(1)

    print_success("Converted successfully.", input_path=src, output_path=out)


# ---------------------------------------------------------------------------
# mp4-to-mp3
# ---------------------------------------------------------------------------


@cli.command(name="mp4-to-mp3")
@click.argument("video_file")
@click.option("--output", "-o", default=None, help="Output MP3 file path.")
@click.option("--bitrate", "-b", default="192k", show_default=True, help="Audio bitrate.")
@click.pass_context
def mp4_to_mp3(ctx: click.Context, video_file: str, output: str | None, bitrate: str) -> None:
    """Extract audio from a video file as MP3.

    \b
    Example:
      tool mp4-to-mp3 video.mp4
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False
    try:
        src = _require_video(video_file)
    except AppError as exc:
        print_error(exc.message)
        sys.exit(1)

    out = Path(output) if output else resolve_output_path(src, ".mp3")
    print_info("Extracting audio → MP3…")

    try:
        run_ffmpeg(
            ["-i", str(src), "-vn", "-acodec", "libmp3lame", "-ab", bitrate, str(out)],
            verbose=verbose,
        )
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)

    print_success("Extracted successfully.", input_path=src, output_path=out)


# ---------------------------------------------------------------------------
# mp4-to-wav
# ---------------------------------------------------------------------------


@cli.command(name="mp4-to-wav")
@click.argument("video_file")
@click.option("--output", "-o", default=None, help="Output WAV file path.")
@click.pass_context
def mp4_to_wav(ctx: click.Context, video_file: str, output: str | None) -> None:
    """Extract audio from a video file as WAV.

    \b
    Example:
      tool mp4-to-wav video.mp4
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False
    try:
        src = _require_video(video_file)
    except AppError as exc:
        print_error(exc.message)
        sys.exit(1)

    out = Path(output) if output else resolve_output_path(src, ".wav")
    print_info("Extracting audio → WAV…")

    try:
        run_ffmpeg(
            ["-i", str(src), "-vn", "-acodec", "pcm_s16le", str(out)],
            verbose=verbose,
        )
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)

    print_success("Extracted successfully.", input_path=src, output_path=out)


# ---------------------------------------------------------------------------
# mp4-to-gif
# ---------------------------------------------------------------------------


@cli.command(name="mp4-to-gif")
@click.argument("video_file")
@click.option("--output", "-o", default=None, help="Output GIF file path.")
@click.option("--fps", default=10, show_default=True, help="Frames per second.")
@click.option("--width", "-w", default=480, show_default=True, help="Output width in pixels.")
@click.pass_context
def mp4_to_gif(
    ctx: click.Context, video_file: str, output: str | None, fps: int, width: int
) -> None:
    """Convert a video to an animated GIF.

    Uses a two-pass palette approach for high-quality output.

    \b
    Example:
      tool mp4-to-gif video.mp4
      tool mp4-to-gif video.mp4 --fps 15 --width 640
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False
    try:
        src = _require_video(video_file)
    except AppError as exc:
        print_error(exc.message)
        sys.exit(1)

    out = Path(output) if output else resolve_output_path(src, ".gif")
    palette = out.with_suffix(".palette.png")
    print_info("Generating palette…")

    try:
        # Pass 1: generate palette
        run_ffmpeg(
            [
                "-i", str(src),
                "-vf", f"fps={fps},scale={width}:-1:flags=lanczos,palettegen",
                str(palette),
            ],
            verbose=verbose,
        )
        print_info("Encoding GIF…")
        # Pass 2: apply palette
        run_ffmpeg(
            [
                "-i", str(src),
                "-i", str(palette),
                "-filter_complex",
                f"fps={fps},scale={width}:-1:flags=lanczos[x];[x][1:v]paletteuse",
                str(out),
            ],
            verbose=verbose,
        )
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)
    finally:
        if palette.exists():
            palette.unlink()

    print_success("Converted successfully.", input_path=src, output_path=out)


# ---------------------------------------------------------------------------
# mp4-to-webm
# ---------------------------------------------------------------------------


@cli.command(name="mp4-to-webm")
@click.argument("video_file")
@click.option("--output", "-o", default=None, help="Output WebM file path.")
@click.option("--quality", "-q", default=33, show_default=True, help="CRF quality (0=best, 63=worst).")
@click.pass_context
def mp4_to_webm(ctx: click.Context, video_file: str, output: str | None, quality: int) -> None:
    """Convert a video to WebM (VP9 + Opus).

    \b
    Example:
      tool mp4-to-webm video.mp4
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False
    try:
        src = _require_video(video_file)
    except AppError as exc:
        print_error(exc.message)
        sys.exit(1)

    out = Path(output) if output else resolve_output_path(src, ".webm")
    print_info("Converting → WebM (VP9)…")

    try:
        run_ffmpeg(
            [
                "-i", str(src),
                "-c:v", "libvpx-vp9",
                "-crf", str(quality),
                "-b:v", "0",
                "-c:a", "libopus",
                str(out),
            ],
            verbose=verbose,
        )
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)

    print_success("Converted successfully.", input_path=src, output_path=out)


# ---------------------------------------------------------------------------
# video-trim
# ---------------------------------------------------------------------------


@cli.command(name="video-trim")
@click.argument("video_file")
@click.argument("start")
@click.argument("end")
@click.option("--output", "-o", default=None, help="Output file path.")
@click.pass_context
def video_trim(ctx: click.Context, video_file: str, start: str, end: str, output: str | None) -> None:
    """Trim a video from START to END (MM:SS or HH:MM:SS).

    \b
    Example:
      tool video-trim video.mp4 00:10 00:30
      tool video-trim video.mp4 01:00:00 01:05:30
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False
    try:
        src = _require_video(video_file)
        start_sec = parse_time(start)
        end_sec = parse_time(end)
    except AppError as exc:
        print_error(exc.message)
        sys.exit(1)
    except ValueError as exc:
        print_error("Invalid time format.", reason=str(exc))
        sys.exit(1)

    if end_sec <= start_sec:
        print_error("END must be after START.")
        sys.exit(1)

    duration = end_sec - start_sec
    out = Path(output) if output else resolve_output_path(
        src, src.suffix, stem_override=f"{src.stem}_trimmed"
    )
    print_info(f"Trimming {start} → {end} ({duration:.1f}s)…")

    try:
        run_ffmpeg(
            [
                "-i", str(src),
                "-ss", str(start_sec),
                "-t", str(duration),
                "-c", "copy",
                str(out),
            ],
            verbose=verbose,
        )
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)

    print_success("Trimmed successfully.", input_path=src, output_path=out)


# ---------------------------------------------------------------------------
# video-resize
# ---------------------------------------------------------------------------


@cli.command(name="video-resize")
@click.argument("video_file")
@click.argument("dimensions")
@click.option("--output", "-o", default=None, help="Output file path.")
@click.pass_context
def video_resize(ctx: click.Context, video_file: str, dimensions: str, output: str | None) -> None:
    """Resize a video to DIMENSIONS (WxH).

    Width and height must both be divisible by 2 (H.264 requirement).
    If your target dimension is odd, it will be rounded down.

    \b
    Example:
      tool video-resize video.mp4 1280x720
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False
    try:
        src = _require_video(video_file)
        w, h = _parse_dims(dimensions)
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)

    # H.264 requires dimensions divisible by 2
    w = w if w % 2 == 0 else w - 1
    h = h if h % 2 == 0 else h - 1

    out = Path(output) if output else resolve_output_path(
        src, src.suffix, stem_override=f"{src.stem}_{w}x{h}"
    )
    print_info(f"Resizing to {w}×{h}…")

    try:
        run_ffmpeg(
            [
                "-i", str(src),
                "-vf", f"scale={w}:{h}",
                "-c:a", "copy",
                str(out),
            ],
            verbose=verbose,
        )
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)

    print_success(f"Resized to {w}×{h}.", input_path=src, output_path=out)


# ---------------------------------------------------------------------------
# video-compress
# ---------------------------------------------------------------------------


@cli.command(name="video-compress")
@click.argument("video_file")
@click.option("--output", "-o", default=None, help="Output file path.")
@click.option(
    "--crf",
    default=28,
    show_default=True,
    help="H.264 CRF value (0=lossless, 51=worst). Default 28 gives good compression.",
)
@click.pass_context
def video_compress(ctx: click.Context, video_file: str, output: str | None, crf: int) -> None:
    """Compress a video using H.264 (libx264).

    \b
    Example:
      tool video-compress video.mp4
      tool video-compress video.mp4 --crf 24
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False
    try:
        src = _require_video(video_file)
    except AppError as exc:
        print_error(exc.message)
        sys.exit(1)

    out = Path(output) if output else resolve_output_path(
        src, src.suffix, stem_override=f"{src.stem}_compressed"
    )
    orig_size = src.stat().st_size
    print_info(f"Compressing with CRF={crf}…")

    try:
        run_ffmpeg(
            [
                "-i", str(src),
                "-c:v", "libx264",
                "-crf", str(crf),
                "-preset", "medium",
                "-c:a", "aac",
                "-b:a", "128k",
                str(out),
            ],
            verbose=verbose,
        )
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)

    new_size = out.stat().st_size
    ratio = (1 - new_size / orig_size) * 100 if orig_size else 0
    print_success(
        f"Compressed ({ratio:.1f}% smaller).",
        input_path=src,
        output_path=out,
    )


# ---------------------------------------------------------------------------
# media-convert (Universal Audio / Video converter)
# ---------------------------------------------------------------------------


@cli.command(name="media-convert")
@click.argument("input_file")
@click.argument("target_format")
@click.option("--output", "-o", default=None, help="Output file path.")
@click.pass_context
def media_convert(
    ctx: click.Context, input_file: str, target_format: str, output: str | None
) -> None:
    """Convert ANY audio or video file to a target format using FFmpeg.

    Supported formats: mp4, mkv, avi, mov, webm, flv, mp3, wav, ogg, flac, m4a, etc.

    \b
    Examples:
      tool media-convert video.mkv mp4
      tool media-convert clip.mov webm
      tool media-convert song.flac mp3
      tool media-convert audio.wav ogg
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False
    try:
        src = _require_video(input_file, label="Input media")
    except AppError as exc:
        print_error(exc.message)
        sys.exit(1)

    target_ext = f".{target_format.lower().lstrip('.')}"
    out = Path(output) if output else resolve_output_path(src, target_ext)
    print_info(f"Converting media → {target_format.upper()}…")

    try:
        run_ffmpeg(
            ["-i", str(src), str(out)],
            verbose=verbose,
        )
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)

    print_success("Converted successfully.", input_path=src, output_path=out)

