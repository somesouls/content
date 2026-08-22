"""Generate gambar background AI: pollinations (gratis) / gemini imagen / none."""
import base64
import urllib.parse
from pathlib import Path

import requests

from ..config import settings


def _aspect(width, height):
    if height > width * 1.4:
        return "9:16"
    if width > height * 1.4:
        return "16:9"
    if height > width:
        return "3:4"
    if width > height:
        return "4:3"
    return "1:1"


def generate_image(prompt, out_path, width=1080, height=1350):
    provider = settings.image_provider
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if provider == "none":
        return None
    try:
        if provider == "gemini":
            return _gemini(prompt, out_path, width, height)
        return _pollinations(prompt, out_path, width, height)
    except Exception as e:  # noqa: BLE001
        print(f"[image] gagal ({provider}): {e}. Lanjut tanpa AI image.")
        return None


def _pollinations(prompt, out_path, width, height):
    enc = urllib.parse.quote(prompt)
    url = (
        "https://image.pollinations.ai/prompt/"
        + enc
        + f"?width={width}&height={height}&nologo=true"
    )
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    out_path.write_bytes(r.content)
    return out_path


def _gemini(prompt, out_path, width, height):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.image_model}:predict?key={settings.gemini_key}"
    )
    body = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1, "aspectRatio": _aspect(width, height)},
    }
    r = requests.post(url, json=body, timeout=180)
    r.raise_for_status()
    b64 = r.json()["predictions"][0]["bytesBase64Encoded"]
    out_path.write_bytes(base64.b64decode(b64))
    return out_path
