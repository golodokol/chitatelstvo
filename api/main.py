from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config.settings import PUBLIC_BASE_URL, ROOT
from api.routes import admin, chest, legal, lesson, pages, progress, quiz, telegram, webhook

app = FastAPI(
    title="Литературная школа онлайн",
    description="Webhook API + личная страница прогресса для родителей",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://chitatelstvo.ru",
        "https://www.chitatelstvo.ru",
        PUBLIC_BASE_URL,
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")

app.include_router(admin.router)
app.include_router(pages.router)
app.include_router(legal.router)
app.include_router(webhook.router)
app.include_router(lesson.router)
app.include_router(progress.router)
app.include_router(chest.router)
app.include_router(quiz.router)
app.include_router(telegram.router)


@app.get("/health")
def health() -> dict:
    from job_queue.redis_queue import queue_length

    return {"status": "ok", "queue_length": queue_length()}
