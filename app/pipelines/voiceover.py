"""Format C: buat video dari aset lama + suara (Coqui XTTS) tanpa rekam ulang."""
import datetime
import shutil
import subprocess
from pathlib import Path

from ..config import settings

_ASSETS = Path(__file__).resolve().parents[2] / "assets"


def synth_voice(text, out_path=None):
    out_path = Path(out_path or (settings.output_dir / "voice.wav"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        from TTS.api import TTS
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(
            "Coqui TTS belum terpasang: pip install TTS. "
            "Untuk clone suaramu, taruh sample di assets/voice/ref.wav"
        ) from e
    ref = _ASSETS / "voice" / "ref.wav"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    kw = {"text": text, "file_path": str(out_path), "language": "id"}
    if ref.exists():
        kw["speaker_wav"] = str(ref)
    tts.tts_to_file(**kw)
    return out_path


def assemble_video(audio_path, background=None, out_path=None):
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg belum terpasang.")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = Path(out_path or (settings.output_dir / f"voiceover-{stamp}.mp4"))
    background = str(background) if background else str(_ASSETS / "bg.png")
    is_video = Path(background).suffix.lower() in (".mp4", ".mov", ".mkv", ".webm")
    common_vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    if is_video:
        cmd = [
            "ffmpeg", "-y", "-stream_loop", "-1", "-i", background, "-i", str(audio_path),
            "-shortest", "-vf", common_vf, "-c:v", "libx264", "-preset", "veryfast",
            "-c:a", "aac", str(out_path),
        ]
    else:
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", background, "-i", str(audio_path),
            "-shortest", "-vf", common_vf, "-c:v", "libx264", "-tune", "stillimage",
            "-preset", "veryfast", "-c:a", "aac", str(out_path),
        ]
    subprocess.run(cmd, check=True)
    return out_path


def make_from_assets(text, background=None):
    """Pakai suara clone kamu + aset video/gambar lama jadi 1 video baru."""
    audio = synth_voice(text)
    return assemble_video(audio, background)
