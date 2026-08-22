"""Penjadwalan: generate (08:00), post (POST_TIME), ebook (mingguan)."""
import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from . import store
from .config import settings
from .pipelines import carousel, ebook, ideas
from .publish import tiktok


def _voiceover_text(idea):
    parts = [idea.get("hook", "")] + list(idea.get("slides", [])) + [idea.get("cta", "")]
    return " ".join(p for p in parts if p)


def job_generate():
    """Buat 1 draf konten harian (carousel / voiceover sesuai DAILY_FORMAT)."""
    idea = ideas.generate_idea()
    if settings.daily_format == "voiceover":
        from .pipelines import voiceover

        asset = voiceover.make_from_assets(_voiceover_text(idea))
        fmt = "voiceover"
    else:
        asset = carousel.render_carousel(idea)
        fmt = "carousel"
    status = "pending" if settings.review_required else "approved"
    item_id = store.add_item(
        pillar=idea.get("pillar"),
        format=fmt,
        title=idea.get("hook"),
        caption=idea.get("caption"),
        hashtags=idea.get("hashtags"),
        asset_path=str(asset),
        status=status,
        scheduled_for=datetime.date.today().isoformat(),
    )
    print(f"[generate] item #{item_id} ({fmt}/{status}): {idea.get('hook')}")
    return item_id


def job_post():
    """Publish konten approved yang dijadwalkan hari ini."""
    today = datetime.date.today().isoformat()
    items = [
        i
        for i in store.list_items("approved")
        if (i.get("scheduled_for") or "").startswith(today)
    ]
    if not items:
        print("[post] tidak ada konten approved untuk hari ini. Lewati.")
        return
    item = items[-1]
    res = tiktok.publish(item)
    store.set_status(item["id"], "posted", posted_at=datetime.datetime.now().isoformat())
    print(f"[post] terkirim #{item['id']}: {item.get('title')} -> {res}")


def job_ebook():
    out = ebook.generate_weekly()
    print(f"[ebook] selesai: {out}")


def start():
    store.init()
    sch = BackgroundScheduler(timezone=settings.timezone)
    sch.add_job(job_generate, CronTrigger(hour=8, minute=0), id="generate", replace_existing=True)
    hh, mm = settings.post_time.split(":")
    sch.add_job(
        job_post,
        CronTrigger(hour=int(hh), minute=int(mm)),
        id="post",
        replace_existing=True,
    )
    sch.add_job(
        job_ebook,
        CronTrigger(day_of_week=settings.ebook_day[:3].lower(), hour=10, minute=0),
        id="ebook",
        replace_existing=True,
    )
    sch.start()
    return sch
