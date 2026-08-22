"""Entrypoint: jalankan scheduler + dashboard review."""
import uvicorn

from app.config import settings
from app.scheduler import start


def main():
    scheduler = start()
    print("=" * 52)
    print(" senior kecemasan — content engine")
    print(f" generate harian : 08:00 {settings.timezone}")
    print(f" auto-post       : {settings.post_time} {settings.timezone}")
    print(f" ebook mingguan  : Sabtu 10:00")
    print(f" dashboard       : http://localhost:{settings.port}")
    print("=" * 52)
    try:
        uvicorn.run("app.server:app", host=settings.host, port=settings.port, reload=False)
    finally:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    main()
