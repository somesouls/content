# senior kecemasan — mesin konten otomatis

Sistem semi-otomatis untuk akun TikTok **@senior kecemasan** (tema: penyintas hidup berantakan & attachment style):

- 1 konten/hari: **carousel**, **klip video**, atau **voiceover** dari aset kamu.
- Auto-posting jam **19.00** (folder `READY_TO_POST` / scheduler pihak ketiga, atau TikTok API).
- Dashboard **review** untuk approve dari HP sebelum tayang.
- Generator **ebook bergambar mingguan** (PDF).

> ⚠️ Tema mental health: konten wajib edukatif & suportif, BUKAN diagnosis/terapi. Disclaimer + kontak darurat (119 ext 8) otomatis muncul di slide penutup. Tetap review sebelum posting.

## Cara pakai (di PC-GPU kamu)

```bash
git clone https://github.com/somesouls/content.git
cd content
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env         # lalu isi konfigurasimu
python run.py
```

Dashboard review: http://localhost:8000

### Alur harian
1. **08:00** sistem generate draf konten → status `pending`.
2. Kamu buka dashboard, klik **Approve** (atau Reject) dari HP.
3. **19.00** konten approved otomatis dipublish.

Untuk full-otomatis tanpa review, set `REVIEW_REQUIRED=false` di `.env` (tidak disarankan untuk topik mental health).

## Konfigurasi LLM (pilih di `.env`)
- `LLM_PROVIDER=fallback` — jalan tanpa API (template bawaan, buat tes cepat).
- `LLM_PROVIDER=azure` — isi `AZURE_OPENAI_*` (kamu sudah familiar).
- `LLM_PROVIDER=ollama` — model lokal di GPU (`OLLAMA_MODEL=qwen2.5:7b`).

## Format konten
- **Carousel** (default, paling aman) — Pillow, tanpa dependensi berat.
- **Klip video** (`app/pipelines/clip.py`) — yt-dlp + ffmpeg. **Default hanya video Creative Commons** dan **selalu menambahkan kredit sumber** di layar + file `attribution.txt`. Kredit saja TIDAK memberi lisensi hak cipta — pakai konten milikmu / berlisensi / CC.
- **Voiceover** (`app/pipelines/voiceover.py`) — Coqui XTTS (bisa clone **suaramu sendiri** dari `assets/voice/ref.wav`) + ffmpeg. "Tanpa rekam ulang" pakai aset lama kamu.

## Ebook mingguan
Tiap Sabtu 10:00 → outline → draf per bab → (opsional) PDF via WeasyPrint. Output di `output/ebook-YYYY-MM-DD/`. **Edit dulu untuk akurasi & empati** sebelum dijual.

## Auto-posting TikTok
- **manual** (default): konten approved dipindah ke `output/READY_TO_POST/`. Upload manual atau sambungkan scheduler (Metricool/Publer/Buffer).
- **api**: isi `TIKTOK_ACCESS_TOKEN`, set `TIKTOK_PROVIDER=api`, lalu lengkapi `app/publish/tiktok.py` sesuai TikTok Content Posting API (butuh approval developer).

## Struktur
```
run.py                 # start scheduler + dashboard
app/
  config.py            # baca .env + config.yaml
  llm.py               # Azure / Ollama / fallback
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
