"""Penyimpanan & log konten (SQLite)."""
import datetime
import json
import sqlite3

from .config import settings

DB = settings.data_dir / "content.db"


def _conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init():
    with _conn() as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT,
                pillar TEXT,
                format TEXT,
                title TEXT,
                caption TEXT,
                hashtags TEXT,
                asset_path TEXT,
                status TEXT DEFAULT 'pending',
                scheduled_for TEXT,
                posted_at TEXT,
                meta TEXT
            )"""
        )


def add_item(**kw):
    kw.setdefault("created_at", datetime.datetime.now().isoformat())
    keys = ",".join(kw.keys())
    ph = ",".join("?" for _ in kw)
    vals = tuple(json.dumps(v) if isinstance(v, (list, dict)) else v for v in kw.values())
    with _conn() as c:
        cur = c.execute(f"INSERT INTO content ({keys}) VALUES ({ph})", vals)
        return cur.lastrowid


def set_status(item_id, status, **extra):
    fields = {"status": status, **extra}
    sets = ",".join(f"{k}=?" for k in fields)
    with _conn() as c:
        c.execute(f"UPDATE content SET {sets} WHERE id=?", (*fields.values(), item_id))


def get(item_id):
    with _conn() as c:
        r = c.execute("SELECT * FROM content WHERE id=?", (item_id,)).fetchone()
        return dict(r) if r else None


def list_items(status=None):
    q = "SELECT * FROM content"
    args = ()
    if status:
        q += " WHERE status=?"
        args = (status,)
    q += " ORDER BY id DESC"
    with _conn() as c:
        return [dict(r) for r in c.execute(q, args).fetchall()]
