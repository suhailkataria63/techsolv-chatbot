from fastapi import FastAPI

from .config import settings


app = FastAPI(title=settings.app_name)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Social video RAG API is running."}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "social-video-rag-api",
    }
