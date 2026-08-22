"""Format B: potong klip dari video (yt-dlp + ffmpeg) + kredit sumber + subtitle.

DEFAULT hanya mengizinkan video Creative Commons. Kredit sumber SELALU
ditambahkan (overlay + attribution.txt). Kredit TIDAK memberi lisensi hak cipta;
gunakan konten milikmu / berlisensi / CC.
"""
import datetime
import json
import shutil
import subprocess
from pathlib import Path

from ..config import settings


def _make_credit_png(text, path, width=1080):
    from PIL import Image, ImageDraw, ImageFont

    h = 120
    img = Image.new("RGBA", (width, h), (0, 0, 0, 150))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 30)
    except Exception:  # noqa: BLE001
        font = ImageFont.load_default()
    d.text((30, 42), text[:80], font=font, fill=(255, 255, 255, 255))
    img.save(path)


def clip_from_youtube(url, start="00:00:05", duration=45, only_creative_commons=True):
    if not shutil.which("yt-dlp") or not shutil.which("ffmpeg"):
        raise RuntimeError("Butuh yt-dlp & ffmpeg terpasang.")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    work = settings.output_dir / f"clip-{stamp}"
    work.mkdir(parents=True, exist_ok=True)

    meta = json.loads(subprocess.check_output(["yt-dlp", "-J", url]).decode())
    lic = (meta.get("license") or "").lower()
    if only_creative_commons and "creative commons" not in lic:
        raise PermissionError(
            f"Video ini bukan Creative Commons (license={meta.get('license')!r}). "
            "Menyalin ulang berisiko melanggar hak cipta. Pakai konten milikmu/berlisensi, "
            "atau set only_creative_commons=False hanya jika kamu benar-benar punya izin."
        )

    credit = f"Sumber: {meta.get('uploader', '?')} - {meta.get('webpage_url', url)}"
    (work / "attribution.txt").write_text(credit + "\n", encoding="utf-8")

    src = work / "src.mp4"
    subprocess.run(["yt-dlp", "-f", "mp4", "-o", str(src), url], check=True)

    credit_png = work / "credit.png"
    _make_credit_png(credit, credit_png)

    out = work / "clip.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-ss", str(start), "-t", str(duration), "-i", str(src),
            "-i", str(credit_png),
            "-filter_complex",
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[v];"
            "[v][1:v]overlay=0:H-h-80[vo]",
            "-map", "[vo]", "-map", "0:a?",
            "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac",
            str(out),
        ],
        check=True,
    )

    final = out
    try:
        from . import subtitles

        final = subtitles.add_subtitles(out)
    except Exception as e:  # noqa: BLE001
        print(f"[clip] subtitle dilewati: {e}")
    return final
