# senior kecemasan — mesin konten otomatis

Sistem semi-otomatis untuk akun TikTok **@senior kecemasan** (tema: penyintas hidup berantakan & attachment style):

- 1 konten/hari: **carousel**, **klip video**, atau **voiceover** dari aset kamu.
- Auto-posting jam **19.00** (folder `READY_TO_POST` / scheduler pihak ketiga, atau TikTok API).
- Dashboard **review** untuk approve dari HP sebelum tayang.
- Generator **ebook bergambar mingguan** (PDF).

> ⚠️ Tema mental health: konten wajib edukatif & suportif, BUKAN diagnosis/terapi. Disclaimer + kontak darurat (119 ext 8) otomatis muncul di slide penutup. Tetap review sebelum posting.

## 1) Install (di PC-GPU kamu)

```bash
git clone https://github.com/somesouls/content.git
cd content
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## 2) Isi API key di `.env`

| Kebutuhan | Env | Cara dapat |
| --- | --- | --- |
| Teks (script/ide/ebook) | `GEMINI_API_KEY` | https://aistudio.google.com/app/apikey |
| Suara (voiceover) | `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` | https://elevenlabs.io |
| Posting API (opsional) | `TIKTOK_ACCESS_TOKEN` | https://developers.tiktok.com |

Default `LLM_PROVIDER=gemini` dan `VOICE_PROVIDER=elevenlabs`. Alternatif: `azure`, `ollama` (LLM lokal di GPU), atau `xtts` (voice clone lokal). Set `LLM_PROVIDER=fallback` untuk tes tanpa API.

## 3) Tes cepat (buktikan jalan)

```bash
python selftest.py           # generate ide (LLM) + render carousel PNG
python selftest.py --voice   # sekalian tes TTS
```
Slide muncul di `output/carousel-*/`.

## 4) Jalankan sistem

```bash
python run.py
```
Dashboard: http://localhost:8000

### Alur harian
1. **08:00** sistem generate draf → status `pending`.
2. Kamu **Approve/Reject** dari dashboard (HP).
3. **19.00** konten approved otomatis dipublish.

Full-otomatis tanpa review: set `REVIEW_REQUIRED=false` (tidak disarankan untuk topik mental health).

## Format konten
- **Carousel** (default, paling aman) — Pillow, tanpa dependensi berat.
- **Klip video** (`app/pipelines/clip.py`) — yt-dlp + ffmpeg. **Default hanya video Creative Commons** + **kredit sumber** otomatis (overlay + `attribution.txt`). Kredit TIDAK memberi lisensi hak cipta — pakai konten milikmu / berlisensi / CC.
- **Voiceover** (`app/pipelines/voiceover.py`) — ElevenLabs (atau XTTS lokal untuk clone suaramu) + ffmpeg. "Tanpa rekam ulang" pakai aset lama kamu.

## Ebook mingguan
Tiap Sabtu 10:00 → outline → draf per bab (LLM) → PDF (WeasyPrint, opsional). Output di `output/ebook-*/`. **Edit dulu untuk akurasi & empati** sebelum dijual.

## Auto-posting TikTok
- **manual** (default): konten approved dipindah ke `output/READY_TO_POST/`. Upload manual / scheduler (Metricool/Publer/Buffer).
- **api**: set `TIKTOK_PROVIDER=api` + `TIKTOK_ACCESS_TOKEN`, lalu lengkapi `app/publish/tiktok.py` sesuai TikTok Content Posting API (butuh approval developer).

## Struktur
```
run.py                 # start scheduler + dashboard
selftest.py            # cek cepat pipeline
app/
  config.py            # baca .env + config.yaml
  llm.py               # gemini / azure / ollama / fallback
  scheduler.py         # jadwal generate (08:00), post (19:00), ebook (Sabtu)
  server.py            # dashboard review (FastAPI)
  store.py             # sqlite log konten
  review.py
  pipelines/           # ideas, carousel, clip, voiceover, ebook
  publish/tiktok.py
prompts/               # persona & instruksi ebook
templates/review.html
config.yaml            # identitas akun + content pillars
```

## Catatan legal & etika
- Hak cipta: jangan repost video/musik orang tanpa izin.
- Mental health: jangan diagnosa / janji sembuh; disclaimer + kontak 119 ext 8 sudah otomatis.
- Suara/wajah: hanya milikmu sendiri.
- Ikuti label konten AI TikTok bila relevan.
