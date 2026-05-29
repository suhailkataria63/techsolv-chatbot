from fastapi import FastAPI, HTTPException

from .config import settings
from .instagram_service import analyze_instagram_reel
from .models import VideoAnalysisResponse, VideoUrlRequest
from .youtube_service import analyze_youtube_video


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


@app.post("/api/videos/youtube/analyze", response_model=VideoAnalysisResponse)
def analyze_youtube(request: VideoUrlRequest) -> VideoAnalysisResponse:
    try:
        return analyze_youtube_video(request.url)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/videos/instagram/analyze", response_model=VideoAnalysisResponse)
def analyze_instagram(request: VideoUrlRequest) -> VideoAnalysisResponse:
    try:
        return analyze_instagram_reel(request.url)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
