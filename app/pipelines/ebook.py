"""Generator ebook bergambar mingguan."""
import datetime
import random
from pathlib import Path

from ..config import settings
from ..llm import chat, generate_json

ROOT = Path(__file__).resolve().parents[2]
OUTLINE_SYSTEM = (ROOT / "prompts" / "ebook_outline.txt").read_text(encoding="utf-8")

THEMES = [
    "Anxious attachment & overthinking",
    "Avoidant attachment & jarak emosi",
    "Inner child & luka masa kecil",
    "Bangkit dari hidup berantakan",
    "Batasan sehat (boundaries)",
]

FALLBACK_OUTLINE = {
    "title": "Pelukan untuk yang Sedang Berantakan",
    "chapters": [
        "Kenapa kamu selalu overthinking",
        "Akar pola attachment-mu",
        "Mengenali pemicu",
        "Cara menenangkan diri",
        "Latihan 7 hari",
        "Pesan penutup",
    ],
}


def generate_weekly(theme=None, heavy=False):
    theme = theme or random.choice(THEMES)
    pages = "100-200" if heavy else "50-100"
    outline = generate_json(
        OUTLINE_SYSTEM, f"Tema: {theme}. Target {pages} halaman. Balas JSON."
    ) or FALLBACK_OUTLINE

    parts = [
        f"# {outline.get('title', 'Ebook')}\n",
        f"_Tema: {theme}_\n",
        "> Konten edukatif & suportif, bukan pengganti bantuan profesional. "
        "Butuh bantuan segera? Hubungi 119 ext 8.\n",
    ]
    for ch in outline.get("chapters", FALLBACK_OUTLINE["chapters"]):
        body = chat(
            "Kamu penulis buku self-help empatik berbahasa Indonesia.",
            f"Tulis isi bab '{ch}' untuk buku bertema '{theme}'. "
            "Hangat, jelas, ada contoh nyata & 1 latihan kecil. 400-700 kata.",
        )
        parts.append(f"\n## {ch}\n\n{body or '_(draf kosong — aktifkan LLM atau isi manual)_'}\n")

    md = "\n".join(parts)
    out = settings.output_dir / f"ebook-{datetime.date.today().isoformat()}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "book.md").write_text(md, encoding="utf-8")
    _render_pdf(md, out)
    return out


def _render_pdf(md, out_dir):
    try:
        import markdown
        import weasyprint

        html = "<meta charset='utf-8'>" + markdown.markdown(md, extensions=["extra"])
        weasyprint.HTML(string=html).write_pdf(str(out_dir / "book.pdf"))
    except Exception as e:  # noqa: BLE001
        (out_dir / "book.html").write_text("<meta charset='utf-8'>" + md, encoding="utf-8")
        print(f"[ebook] PDF dilewati ({e}). Tersimpan .md/.html. Install: pip install markdown weasyprint")
