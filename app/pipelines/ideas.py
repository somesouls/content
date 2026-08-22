"""Generate ide + script konten (hook, slides dinamis, CTA, caption, visual)."""
import random
from pathlib import Path

from ..config import settings
from ..llm import generate_json

ROOT = Path(__file__).resolve().parents[2]
SYSTEM = (ROOT / "prompts" / "system_prompt.txt").read_text(encoding="utf-8")

FALLBACK = [
    {
        "hook": "Tanda kamu punya anxious attachment",
        "slides": [
            "Kamu baca ulang chat-mu sendiri, takut salah kata.",
            "Dia telat balas 1 jam, kepalamu sudah bikin 10 skenario putus.",
            "Kamu minta maaf untuk hal yang bukan salahmu, biar aman.",
            "Sendirian rasanya seperti ditinggalkan, bukan istirahat.",
        ],
        "cta": "Simpan ini. Kamu nggak berlebihan, kamu cuma belum merasa aman.",
        "caption": "Anxious attachment itu bukan aib. Ini pola yang bisa dilatih ulang pelan-pelan.",
        "hashtags": ["#attachmentstyle", "#anxiousattachment", "#healing", "#selfawareness", "#mentalhealthid"],
        "visual_prompt": "moody dark bedroom at night, phone glow, lonely aesthetic, cinematic, no text",
    },
    {
        "hook": "Hidup berantakan bukan akhir cerita",
        "slides": [
            "Berantakan artinya kamu masih di tengah proses, bukan gagal.",
            "Kamu boleh mulai dari 1 hal kecil hari ini.",
            "Rapi itu hasil ratusan keputusan kecil, bukan 1 keajaiban.",
            "Penyintas bukan yang nggak pernah jatuh, tapi yang bangun lagi.",
        ],
        "cta": "Satu langkah kecil hari ini sudah cukup. Beneran.",
        "caption": "Buat kamu yang lagi ngerasa semuanya berantakan. Pelan-pelan aja ya.",
        "hashtags": ["#penyintas", "#healingjourney", "#selfhealing", "#tumbuh", "#mentalhealthid"],
        "visual_prompt": "soft morning light through window, messy cozy room, hopeful mood, cinematic, no text",
    },
]


def generate_idea(pillar=None):
    pillar = pillar or random.choice(settings.pillars or ["healing"])
    prompt = (
        f"Buat 1 konten carousel untuk pillar: '{pillar}'. "
        "Tentukan sendiri jumlah slide yang paling pas (4-8) sesuai bobot topik. "
        "Balas HANYA JSON sesuai format (termasuk field visual_prompt)."
    )
    data = generate_json(SYSTEM, prompt)
    if not data or "hook" not in data or not data.get("slides"):
        data = dict(random.choice(FALLBACK))
    data["pillar"] = pillar
    data.setdefault("hashtags", [])
    return data
