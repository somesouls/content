"""Render carousel jadi slide PNG 1080x1350 (Pillow), opsional background AI."""
import datetime
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ..config import settings

W, H = 1080, 1350
BG = (17, 18, 23)
FG = (238, 238, 245)
MUTED = (150, 150, 160)
ACCENT = (255, 138, 101)
DISCLAIMER = (
    "Konten edukatif, bukan pengganti bantuan profesional. "
    "Butuh bantuan? Hubungi 119 ext 8."
)
_FONTS = Path(__file__).resolve().parents[2] / "assets" / "fonts"


def _font(size, bold=False):
    names = ["Inter-Bold.ttf", "DejaVuSans-Bold.ttf"] if bold else ["Inter-Regular.ttf", "DejaVuSans.ttf"]
    for n in names:
        p = _FONTS / n
        if p.exists():
            return ImageFont.truetype(str(p), size)
    for sysname in (["DejaVuSans-Bold.ttf"] if bold else ["DejaVuSans.ttf"]):
        try:
            return ImageFont.truetype(sysname, size)
        except Exception:  # noqa: BLE001
            pass
    return ImageFont.load_default()


def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _prep_bg(bg_path):
    """Cover-crop ke 1080x1350 lalu gelapkan agar teks terbaca."""
    img = Image.open(bg_path).convert("RGB")
    scale = max(W / img.width, H / img.height)
    img = img.resize((int(img.width * scale), int(img.height * scale)))
    left = (img.width - W) // 2
    top = (img.height - H) // 2
    img = img.crop((left, top, left + W, top + H))
    return Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), 0.55)


def _slide(text, idx, total, kind="body", bg=None):
    img = _prep_bg(bg) if bg else Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=ACCENT)
    margin = 90
    size = 78 if kind == "hook" else 58
    font = _font(size, bold=(kind != "body"))
    lines = _wrap(d, text, font, W - 2 * margin)
    line_h = size + 20
    y = (H - line_h * len(lines)) // 2
    for ln in lines:
        d.text((margin, y), ln, font=font, fill=FG)
        y += line_h
    ft = _font(30)
    d.text((margin, H - 150), settings.account.get("handle", "@senior kecemasan"), font=ft, fill=ACCENT)
    d.text((W - margin - 80, H - 150), f"{idx}/{total}", font=ft, fill=MUTED)
    if kind == "cta":
        dfont = _font(24)
        for i, ln in enumerate(_wrap(d, DISCLAIMER, dfont, W - 2 * margin)):
            d.text((margin, H - 300 + i * 32), ln, font=dfont, fill=MUTED)
    return img


def render_carousel(idea, out_dir=None):
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path(out_dir or (settings.output_dir / f"carousel-{stamp}"))
    out_dir.mkdir(parents=True, exist_ok=True)

    bg_path = None
    if settings.image_provider != "none":
        try:
            from . import images

            vp = idea.get("visual_prompt") or (
                f"moody aesthetic background, {idea.get('pillar', '')}, dark cinematic, "
                "soft grain, calm, no text, no words, no letters"
            )
            bg_path = images.generate_image(vp, out_dir / "bg.png", W, H)
        except Exception as e:  # noqa: BLE001
            print(f"[carousel] bg AI dilewati: {e}")
            bg_path = None

    parts = [("hook", idea.get("hook", ""))]
    parts += [("body", s) for s in idea.get("slides", [])]
    parts.append(("cta", idea.get("cta", "")))
    total = len(parts)
    for i, (kind, text) in enumerate(parts, start=1):
        _slide(text, i, total, kind, bg=bg_path).save(out_dir / f"slide-{i:02d}.png")
    caption = (idea.get("caption", "") + "\n\n" + " ".join(idea.get("hashtags", []))).strip()
    (out_dir / "caption.txt").write_text(caption, encoding="utf-8")
    return out_dir


def slides_to_video(slide_dir, seconds=3, out_path=None):
    """Ubah slide PNG jadi video vertikal 1080x1920 (buat TikTok tanpa hosting)."""
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg belum terpasang.")
    slide_dir = Path(slide_dir)
    slides = sorted(slide_dir.glob("slide-*.png"))
    if not slides:
        raise RuntimeError("Tidak ada slide untuk dijadikan video.")
    concat = slide_dir / "slides.txt"
    lines = []
    for s in slides:
        lines.append(f"file '{s.name}'")
        lines.append(f"duration {seconds}")
    lines.append(f"file '{slides[-1].name}'")
    concat.write_text("\n".join(lines), encoding="utf-8")
    out_path = Path(out_path or (slide_dir / "carousel.mp4"))
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
            "-vf", "scale=1080:1350,pad=1080:1920:0:285:color=0x111117,format=yuv420p",
            "-r", "30", str(out_path),
        ],
        check=True,
        cwd=str(slide_dir),
    )
    return out_path
