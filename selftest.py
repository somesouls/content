"""Cek cepat pipeline tanpa posting.

Jalankan:  python selftest.py
- Tes LLM (sesuai LLM_PROVIDER di .env) -> generate ide.
- Render carousel jadi PNG.
- Opsional: tes TTS jika --voice.
"""
import sys

from app.config import settings
from app.pipelines import carousel, ideas


def main():
    print(f"LLM_PROVIDER = {settings.llm_provider}")
    idea = ideas.generate_idea()
    print(f"Hook: {idea.get('hook')}")
    out = carousel.render_carousel(idea)
    slides = sorted(out.glob("slide-*.png"))
    print(f"OK. {len(slides)} slide dibuat di: {out}")
    for p in slides:
        print(" -", p)

    if "--voice" in sys.argv:
        from app.pipelines import voiceover

        print(f"\nVOICE_PROVIDER = {settings.voice_provider}")
        audio = voiceover.synth_voice(idea.get("hook", "halo, ini tes suara."))
        print("Audio:", audio)


if __name__ == "__main__":
    main()
