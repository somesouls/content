"""Dashboard review (FastAPI)."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

from . import review, store
from .config import settings
from .publish import tiktok
from .scheduler import job_generate

ROOT = Path(__file__).resolve().parent.parent
store.init()

app = FastAPI(title="senior kecemasan engine")
settings.output_dir.mkdir(exist_ok=True)
app.mount("/output", StaticFiles(directory=str(settings.output_dir)), name="output")
env = Environment(loader=FileSystemLoader(str(ROOT / "templates")), autoescape=True)


def _preview(item):
    if not item.get("asset_path"):
        return None
    p = Path(item["asset_path"])
    if p.is_dir():
        slides = sorted(p.glob("slide-*.png"))
        p = slides[0] if slides else None
    if not p or not p.exists():
        return None
    try:
        return "/output/" + str(p.relative_to(settings.output_dir)).replace("\\\\", "/")
    except Exception:  # noqa: BLE001
        return None


@app.get("/", response_class=HTMLResponse)
def home():
    items = store.list_items()
    for it in items:
        it["preview"] = _preview(it)
    return env.get_template("review.html").render(items=items, account=settings.account)


@app.post("/approve/{item_id}")
def approve(item_id: int):
    review.approve(item_id)
    return RedirectResponse("/", status_code=303)


@app.post("/reject/{item_id}")
def reject(item_id: int):
    review.reject(item_id)
    return RedirectResponse("/", status_code=303)


@app.post("/generate")
def generate_now():
    job_generate()
    return RedirectResponse("/", status_code=303)


@app.post("/post-now/{item_id}")
def post_now(item_id: int):
    item = store.get(item_id)
    if item:
        tiktok.publish(item)
        store.set_status(item_id, "posted")
    return RedirectResponse("/", status_code=303)
