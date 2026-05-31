from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from .chat.chat_service import answer_question
from .chat.stream_service import stream_answer
from .config import settings
from .instagram_service import analyze_instagram_reel
from .models import ChatRequest, ChatResponse, VideoAnalysisResponse, VideoUrlRequest
from .rag.ingest_service import ingest_video_transcript
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
        video = analyze_youtube_video(request.url)
        video.rag_ingestion = ingest_video_transcript(video)
        return video
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/videos/instagram/analyze", response_model=VideoAnalysisResponse)
def analyze_instagram(request: VideoUrlRequest) -> VideoAnalysisResponse:
    try:
        video = analyze_instagram_reel(request.url)
        video.rag_ingestion = ingest_video_transcript(video)
        return video
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/chat/query", response_model=ChatResponse)
def query_chat(request: ChatRequest) -> ChatResponse:
    try:
        return answer_question(request.session_id, request.message)
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Could not answer chat query: {error}",
        ) from error


@app.post("/api/chat/stream")
def stream_chat(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        stream_answer(request.session_id, request.message),
        media_type="text/plain",
    )
