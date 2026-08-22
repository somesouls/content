"""Konfigurasi: baca .env + config.yaml."""
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent


def _load_yaml():
    p = ROOT / "config.yaml"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


_YAML = _load_yaml()


class Settings:
    # ==== LLM (teks) ==== provider: gemini | azure | ollama | fallback
    llm_provider = os.getenv("LLM_PROVIDER", "fallback")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_key = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01")
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    # ==== Voice / TTS ==== provider: elevenlabs | xtts
    voice_provider = os.getenv("VOICE_PROVIDER", "elevenlabs")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "")
    elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "")
    elevenlabs_model = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")

    # ==== Images (background AI) ==== provider: pollinations | gemini | none
    image_provider = os.getenv("IMAGE_PROVIDER", "pollinations")
    image_model = os.getenv("IMAGE_MODEL", "imagen-3.0-generate-002")

    # ==== Subtitles (auto) ====
    subtitles_enabled = os.getenv("SUBTITLES_ENABLED", "true").lower() == "true"
    whisper_model = os.getenv("WHISPER_MODEL", "small")

    # ==== Format harian ==== carousel | voiceover
    daily_format = os.getenv("DAILY_FORMAT", "carousel")

    # ==== Posting ====
    post_time = os.getenv("POST_TIME", "19:00")
    timezone = os.getenv("TIMEZONE", "Asia/Jakarta")
    tiktok_provider = os.getenv("TIKTOK_PROVIDER", "manual")
    tiktok_token = os.getenv("TIKTOK_ACCESS_TOKEN", "")
    # privacy: SELF_ONLY | PUBLIC_TO_EVERYONE | MUTUAL_FOLLOW_FRIENDS | FOLLOWER_OF_CREATOR
    tiktok_privacy = os.getenv("TIKTOK_PRIVACY", "SELF_ONLY")
    public_base_url = os.getenv("PUBLIC_BASE_URL", "")

    # ==== Server ====
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    review_required = os.getenv("REVIEW_REQUIRED", "true").lower() == "true"

    # ==== Paths ====
    output_dir = ROOT / "output"
    data_dir = ROOT / "data"

    # ==== From YAML ====
    account = _YAML.get("account", {})
    pillars = _YAML.get("pillars", [])
    ebook_day = (_YAML.get("ebook", {}) or {}).get("day", "saturday")


settings = Settings()
settings.output_dir.mkdir(exist_ok=True)
settings.data_dir.mkdir(exist_ok=True)
