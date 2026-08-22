# senior kecemasan — mesin konten otomatis

Sistem semi-otomatis untuk akun TikTok **@senior kecemasan** (tema: penyintas hidup berantakan & attachment style).

**Semua otomatis:** jumlah slide, hook, CTA, caption, hashtag, background AI, subtitle, dan posting jam 19.00 — semua digenerate & dijadwalkan sendiri. Kamu tinggal review (opsional) dari HP.

- 1 konten/hari: **carousel** atau **voiceover** (bisa dirotasi).
- **Background AI** otomatis (Pollinations gratis / Gemini Imagen).
- **Auto-subtitle** (Whisper) untuk klip & voiceover.
- **Auto-posting** ke TikTok via Content Posting API (video FILE_UPLOAD / foto PULL_FROM_URL).
- Generator **ebook bergambar mingguan** (PDF).

> ⚠️ Tema mental health: konten wajib edukatif & suportif, BUKAN diagnosis/terapi. Disclaimer + kontak 119 ext 8 otomatis di slide penutup. Review sebelum publik.

## 1) Install
```bash
git clone https://github.com/somesouls/content.git
cd content
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt   # butuh ffmpeg & (untuk klip) yt-dlp di sistem
cp .env.example .env
```

## 2) Isi `.env`
| Fitur | Env | Catatan |
| --- | --- | --- |
| Teks (ide/script/ebook) | `GEMINI_API_KEY` | aistudio.google.com/app/apikey |
| Suara GRATIS (default) | `VOICE_PROVIDER=xtts` | jalan di GPU-mu; clone suaramu via `assets/voice/ref.wav` |
| Suara premium | `VOICE_PROVIDER=elevenlabs` + key | kuota free kecil |
| Background AI (default) | `IMAGE_PROVIDER=pollinations` | GRATIS, tanpa key |
| Subtitle | `SUBTITLES_ENABLED=true` | Whisper (`faster-whisper`) |
| Auto-post TikTok | `TIKTOK_PROVIDER=api` + `TIKTOK_ACCESS_TOKEN` | lihat bagian TikTok |

## 3) Tes cepat (buktikan jalan)
```bash
python selftest.py           # generate ide (LLM) + background AI + render carousel
python selftest.py --voice   # sekalian tes TTS
```
Hasil di `output/carousel-*/`.

## 4) Jalankan
```bash
python run.py    # scheduler + dashboard
```
Dashboard: http://localhost:8000

### Alur harian otomatis
1. **08:00** — generate draf (carousel/voiceover) + background AI + subtitle → `pending`.
2. Kamu **Approve** dari HP (atau set `REVIEW_REQUIRED=false` untuk full-otomatis).
3. **19.00** — auto-post ke TikTok.
4. **Sabtu 10:00** — ebook mingguan.

## Suara: ElevenLabs vs XTTS (gratis)
- `VOICE_PROVIDER=elevenlabs`: kualitas tinggi, tapi kuota free kecil (harian kemungkinan perlu paket bayar).
- `VOICE_PROVIDER=xtts`: **gratis**, jalan di GPU-mu, dan bisa **clone suaramu** — taruh sample bersih 10-30 detik di `assets/voice/ref.wav`. Butuh `pip install TTS`.

## Auto-subtitle (Whisper)
Aktif default (`SUBTITLES_ENABLED=true`). Untuk klip & voiceover: audio ditranskrip `faster-whisper` (Indonesia) → SRT → di-burn ke video. Atur akurasi via `WHISPER_MODEL`.

## Background AI
`IMAGE_PROVIDER=pollinations` (gratis) atau `gemini` (Imagen). Prompt visual dibuat otomatis oleh LLM (`visual_prompt`), lalu digelapkan agar teks terbaca. `none` untuk mematikan.

## Auto-posting TikTok (Content Posting API)
1. Daftar app di https://developers.tiktok.com, aktifkan scope `video.publish` (+ `photo.publish` jika perlu), dapatkan **access token**.
2. Set `TIKTOK_PROVIDER=api`, `TIKTOK_ACCESS_TOKEN=...`.
3. **Privacy:** app yang belum diaudit TikTok **hanya boleh `SELF_ONLY`** (draft privat). Setelah audit lolos, ganti ke `PUBLIC_TO_EVERYONE`.
4. **Video** pakai FILE_UPLOAD (tanpa hosting). **Carousel foto** butuh URL publik (`PUBLIC_BASE_URL`, arahkan domainmu ke server `/output`). Jika `PUBLIC_BASE_URL` kosong, slide otomatis diubah jadi video lalu diupload sebagai video — tetap full otomatis.

## Format klip video
`app/pipelines/clip.py` — **default hanya video Creative Commons** + kredit sumber otomatis (overlay + `attribution.txt`) + subtitle. Kredit TIDAK memberi lisensi hak cipta; pakai konten milikmu/berlisensi/CC.

## Struktur
```
run.py / selftest.py
app/
  config.py llm.py scheduler.py server.py store.py review.py
  pipelines/  ideas carousel clip voiceover ebook images subtitles
  publish/tiktok.py
prompts/ templates/ config.yaml
```

## Catatan legal & etika
- Hak cipta: jangan repost video/musik orang tanpa izin.
- Mental health: jangan diagnosa/janji sembuh; disclaimer + 119 ext 8 otomatis.
- Suara/wajah: hanya milikmu.
- Patuhi label konten AI TikTok bila relevan.
