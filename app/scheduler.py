"""Penjadwalan: generate (08:00), post (POST_TIME), ebook (mingguan)."""
import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from . import store
from .config import settings
from .pipelines import carousel, ebook, ideas
from .publish import tiktok


def job_generate():
    """Buat 1 draf carousel harian."""
    idea = ideas.generate_idea()
    slide_dir = carousel.render_carousel(idea)
    status = "pending" if settings.review_required else "approved"
    item_id = store.add_item(
        pillar=idea.get("pillar"),
        format="carousel",
        title=idea.get("hook"),
        caption=idea.get("caption"),
        hashtags=idea.get("hashtags"),
        asset_path=str(slide_dir),
        status=status,
        scheduled_for=datetime.date.today().isoformat(),
    )
    print(f"[generate] item #{item_id} ({status}): {idea.get('hook')}")
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
