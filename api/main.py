from fastapi import FastAPI

from api.routes import lesson, progress, telegram, webhook

app = FastAPI(
    title="Литературная школа онлайн",
    description="Webhook API + личная страница прогресса для родителей",
    version="1.0.0",
)

app.include_router(webhook.router)
app.include_router(lesson.router)
app.include_router(progress.router)
app.include_router(telegram.router)


@app.get("/health")
def health() -> dict:
    from job_queue.redis_queue import queue_length

    return {"status": "ok", "queue_length": queue_length()}
