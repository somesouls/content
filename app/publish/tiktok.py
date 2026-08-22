"""Publikasi ke TikTok: manual (folder) atau Content Posting API (direct post).

Catatan penting:
- App yang BELUM di-audit TikTok hanya boleh posting privacy SELF_ONLY (privat).
  Set TIKTOK_PRIVACY=PUBLIC_TO_EVERYONE hanya setелah app-mu lolos audit.
- Video: pakai FILE_UPLOAD (tidak butuh URL publik).
- Carousel foto: TikTok menarik gambar via URL publik (PULL_FROM_URL) -> butuh
  PUBLIC_BASE_URL. Jika kosong, sistem otomatis mengubah slide jadi video lalu
  upload sebagai video (tetap full otomatis tanpa hosting).
"""
import json
import shutil
import time
from pathlib import Path

import requests

from ..config import settings

API = "https://open.tiktokapis.com/v2"


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
    print(f"[tiktok] MANUAL: {dest} siap diupload (manual / scheduler pihak ketiga).")
    return {"mode": "manual", "path": str(dest)}


def _headers():
    return {
        "Authorization": f"Bearer {settings.tiktok_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }


def _caption(item):
    cap = item.get("caption") or item.get("title") or ""
    tags = item.get("hashtags") or ""
    if isinstance(tags, str) and tags.strip().startswith("["):
        try:
            tags = json.loads(tags)
        except Exception:  # noqa: BLE001
            tags = tags
    if isinstance(tags, list):
        tags = " ".join(tags)
    return (str(cap) + " " + str(tags)).strip()[:2200]


def _public_url(path):
    if not settings.public_base_url:
        raise RuntimeError("PUBLIC_BASE_URL kosong.")
    rel = str(Path(path).relative_to(settings.output_dir)).replace("\\", "/")
    return settings.public_base_url.rstrip("/") + "/output/" + rel


def _publish_api(item):
    if not settings.tiktok_token:
        raise RuntimeError("TIKTOK_ACCESS_TOKEN kosong. Daftar TikTok for Developers dulu.")
    asset = Path(item["asset_path"])
    if asset.is_dir():
        if settings.public_base_url:
            return _post_photos(item, asset)
        # Tanpa hosting publik: ubah slide jadi video lalu upload sebagai video.
        from ..pipelines.carousel import slides_to_video

        video = slides_to_video(asset)
        return _post_video(item, video)
    return _post_video(item, asset)


def _post_video(item, video_path):
    video_path = Path(video_path)
    size = video_path.stat().st_size
    init = requests.post(
        f"{API}/post/publish/video/init/",
        headers=_headers(),
        json={
            "post_info": {
                "title": _caption(item),
                "privacy_level": settings.tiktok_privacy,
                "disable_comment": False,
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": size,
                "chunk_size": size,
                "total_chunk_count": 1,
            },
        },
        timeout=60,
    )
    init.raise_for_status()
    d = init.json()["data"]
    upload_url, publish_id = d["upload_url"], d["publish_id"]
    with open(video_path, "rb") as f:
        payload = f.read()
    put = requests.put(
        upload_url,
        headers={
            "Content-Type": "video/mp4",
            "Content-Range": f"bytes 0-{size - 1}/{size}",
        },
        data=payload,
        timeout=600,
    )
    put.raise_for_status()
    return {"mode": "api", "type": "video", "publish_id": publish_id, "status": _poll(publish_id)}


def _post_photos(item, folder):
    slides = sorted(Path(folder).glob("slide-*.png"))
    urls = [_public_url(p) for p in slides]
    init = requests.post(
        f"{API}/post/publish/content/init/",
        headers=_headers(),
        json={
            "post_info": {
                "title": _caption(item),
                "privacy_level": settings.tiktok_privacy,
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "photo_cover_index": 0,
                "photo_images": urls,
            },
            "post_mode": "DIRECT_POST",
            "media_type": "PHOTO",
        },
        timeout=60,
    )
    init.raise_for_status()
    publish_id = init.json()["data"]["publish_id"]
    return {"mode": "api", "type": "photo", "publish_id": publish_id, "status": _poll(publish_id)}


def _poll(publish_id, tries=10, delay=3):
    for _ in range(tries):
        r = requests.post(
            f"{API}/post/publish/status/fetch/",
            headers=_headers(),
            json={"publish_id": publish_id},
            timeout=30,
        )
        if r.ok:
            st = r.json().get("data", {}).get("status")
            if st in ("PUBLISH_COMPLETE", "FAILED"):
                return st
        time.sleep(delay)
    return "PENDING"
