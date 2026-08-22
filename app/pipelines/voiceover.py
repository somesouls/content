"""Format C: video dari aset lama + suara (ElevenLabs / XTTS lokal) + subtitle."""
import datetime
import shutil
import subprocess
from pathlib import Path

import requests

from ..config import settings

_ASSETS = Path(__file__).resolve().parents[2] / "assets"


def synth_voice(text, out_path=None):
    """Dispatch ke provider TTS sesuai .env (elevenlabs | xtts)."""
    if settings.voice_provider == "xtts":
        return _xtts(text, out_path)
    return _elevenlabs(text, out_path)


def _elevenlabs(text, out_path=None):
    out_path = Path(out_path or (settings.output_dir / "voice.mp3"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not settings.elevenlabs_key or not settings.elevenlabs_voice_id:
        raise RuntimeError("Isi ELEVENLABS_API_KEY & ELEVENLABS_VOICE_ID di .env.")
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + settings.elevenlabs_voice_id
    headers = {
        "xi-api-key": settings.elevenlabs_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    body = {
        "text": text,
        "model_id": settings.elevenlabs_model,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    r = requests.post(url, headers=headers, json=body, timeout=180)
    r.raise_for_status()
    out_path.write_bytes(r.content)
    return out_path


def _xtts(text, out_path=None):
    """Gratis, jalan di GPU-mu. Clone suaramu dari assets/voice/ref.wav."""
    out_path = Path(out_path or (settings.output_dir / "voice.wav"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        from TTS.api import TTS
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(
            "Coqui TTS belum terpasang: pip install TTS. "
            "Taruh sample suaramu di assets/voice/ref.wav untuk voice clone."
        ) from e
    ref = _ASSETS / "voice" / "ref.wav"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    kw = {"text": text, "file_path": str(out_path), "language": "id"}
    if ref.exists():
        kw["speaker_wav"] = str(ref)
    else:
        print("[xtts] assets/voice/ref.wav tidak ada -> pakai suara default XTTS.")
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
    """Suara (clone) + aset/bg AI jadi 1 video vertikal + subtitle otomatis."""
    audio = synth_voice(text)
    if background is None and settings.image_provider != "none":
        try:
            from . import images

            bg = settings.output_dir / "vo-bg.png"
            background = images.generate_image(
                "vertical cinematic background, calm, moody, soft grain, no text, no words",
                bg,
                1080,
                1920,
            )
        except Exception as e:  # noqa: BLE001
            print(f"[voiceover] bg AI dilewati: {e}")
    video = assemble_video(audio, background)
    try:
        from . import subtitles

        video = subtitles.add_subtitles(video, audio_for_transcript=audio)
    except Exception as e:  # noqa: BLE001
        print(f"[voiceover] subtitle dilewati: {e}")
    return video
