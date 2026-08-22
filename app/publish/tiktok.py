"""Publikasi ke TikTok: mode manual (folder) atau API."""
import shutil
from pathlib import Path

from ..config import settings


def publish(item, provider=None):
    provider = provider or settings.tiktok_provider
    if provider == "api":
        return _publish_api(item)
    return _publish_manual(item)


def _publish_manual(item):
    ready = settings.output_dir / "READY_TO_POST"
    ready.mkdir(exist_ok=True)
    src = Path(item["asset_path"])
    dest = ready / f"{item['id']:04d}-{src.name}"
    if src.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    else:
        shutil.copy2(src, dest)
    print(f"[tiktok] MANUAL: {dest} siap diupload (manual / via scheduler pihak ketiga).")
    return {"mode": "manual", "path": str(dest)}


def _publish_api(item):
    # TikTok Content Posting API: init -> upload -> publish.
    # Butuh app terdaftar di TikTok for Developers + approval + access token.
    if not settings.tiktok_token:
        raise RuntimeError("TIKTOK_ACCESS_TOKEN kosong. Daftar TikTok for Developers dulu.")
    raise NotImplementedError(
        "Lengkapi alur TikTok Content Posting API di sini sesuai kredensialmu. "
        "Lihat catatan di README bagian Auto-posting TikTok."
    )
