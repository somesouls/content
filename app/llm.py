"""Klien LLM: Gemini (Google AI Studio) / Azure OpenAI / Ollama / fallback."""
import json

import requests

from .config import settings


def chat(system: str, user: str, temperature: float = 0.9) -> str:
    provider = settings.llm_provider
    try:
        if provider == "gemini":
            return _gemini(system, user, temperature)
        if provider == "azure":
            return _azure(system, user, temperature)
        if provider == "ollama":
            return _ollama(system, user, temperature)
    except Exception as e:  # noqa: BLE001
        print(f"[llm] error ({provider}): {e}. Pakai fallback.")
        return ""
    return ""


def _gemini(system, user, temperature):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent?key={settings.gemini_key}"
    )
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"temperature": temperature},
    }
    r = requests.post(url, json=body, timeout=120)
    r.raise_for_status()
    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _azure(system, user, temperature):
    url = (
        f"{settings.azure_endpoint}/openai/deployments/"
        f"{settings.azure_deployment}/chat/completions"
        f"?api-version={settings.azure_api_version}"
    )
    headers = {"api-key": settings.azure_key, "Content-Type": "application/json"}
    body = {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
    }
    r = requests.post(url, headers=headers, json=body, timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def _ollama(system, user, temperature):
    url = f"{settings.ollama_host}/api/chat"
    body = {
        "model": settings.ollama_model,
        "stream": False,
        "options": {"temperature": temperature},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    r = requests.post(url, json=body, timeout=300)
    r.raise_for_status()
    return r.json()["message"]["content"]


def generate_json(system: str, user: str):
    raw = (chat(system, user) or "").strip()
    if not raw:
        return None
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:]
    a, b = raw.find("{"), raw.rfind("}")
    if a != -1 and b != -1:
        raw = raw[a : b + 1]
    try:
        return json.loads(raw)
    except Exception:  # noqa: BLE001
        return None
