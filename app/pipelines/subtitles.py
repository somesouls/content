"""Auto-subtitle: transkrip (faster-whisper) + burn ke video (ffmpeg)."""
import shutil
import subprocess
from pathlib import Path

from ..config import settings


def transcribe(media_path):
    """Kembalikan segmen [(start, end, text)] dari audio/video."""
    try:
        from faster_whisper import WhisperModel
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(
            "faster-whisper belum terpasang: pip install faster-whisper"
        ) from e
    model = WhisperModel(settings.whisper_model, device="auto", compute_type="auto")
    segments, _ = model.transcribe(str(media_path), language="id", vad_filter=True)
    return [(s.start, s.end, s.text.strip()) for s in segments if s.text.strip()]


def _ts(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int((t - int(t)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(segments, path):
    lines = []
    for i, (start, end, text) in enumerate(segments, 1):
        lines += [str(i), f"{_ts(start)} --> {_ts(end)}", text, ""]
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    return path


def burn(video_path, srt_path, out_path=None):
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg belum terpasang.")
    video_path = Path(video_path)
    out_path = Path(out_path or video_path.with_name(video_path.stem + "-sub.mp4"))
    srt = str(srt_path).replace("\\", "/").replace(":", "\\:")
    style = (
        "FontName=DejaVu Sans,FontSize=16,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H80000000,BorderStyle=3,Outline=1,Shadow=0,"
        "Alignment=2,MarginV=130"
    )
    vf = f"subtitles='{srt}':force_style='{style}'"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(video_path), "-vf", vf, "-c:a", "copy", str(out_path)],
        check=True,
    )
    return out_path


def add_subtitles(video_path, audio_for_transcript=None):
    """Transkrip (dari audio bila ada, else video) lalu burn subtitle."""
    if not settings.subtitles_enabled:
        return video_path
    segments = transcribe(audio_for_transcript or video_path)
    if not segments:
        return video_path
    srt = Path(video_path).with_suffix(".srt")
    write_srt(segments, srt)
    return burn(video_path, srt)
