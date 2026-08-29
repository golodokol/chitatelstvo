from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config.settings import PUBLIC_BASE_URL, ROOT
from api.routes import admin, auth, cabinet_api, chest, chest_v1, early_trial, legal, lesson, lesson_v1, max_bot, pages, progress, quiz, telegram, test_lesson, webhook

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

_LLMS = ROOT / "docs" / "course-pages" / "llms.txt"


@app.get("/llms.txt", include_in_schema=False)
def llms_txt() -> FileResponse:
    return FileResponse(_LLMS, media_type="text/plain; charset=utf-8")


app.include_router(admin.router)
app.include_router(pages.router)
app.include_router(legal.router)
app.include_router(webhook.router)
app.include_router(auth.router)
app.include_router(cabinet_api.router)
app.include_router(lesson_v1.router)
app.include_router(chest_v1.router)
app.include_router(lesson.router)
app.include_router(progress.router)
app.include_router(chest.router)
app.include_router(quiz.router)
app.include_router(early_trial.router)
app.include_router(telegram.router)
app.include_router(max_bot.router)
app.include_router(test_lesson.router)


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse(ROOT / "static" / "favicon.png", media_type="image/png")


@app.get("/health")
def health() -> dict:
    from job_queue.redis_queue import queue_length

    return {"status": "ok", "queue_length": queue_length()}
