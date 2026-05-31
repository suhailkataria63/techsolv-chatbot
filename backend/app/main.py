from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from .chat.chat_service import answer_question
from .chat.stream_service import stream_answer
from .config import settings
from .instagram_service import analyze_instagram_reel
from .models import (
    ChatRequest,
    ChatResponse,
    VideoAnalysisResponse,
    VideoUrlRequest,
    WorkspaceRequest,
    WorkspaceResponse,
)
from .rag.ingest_service import ingest_video_transcript
from .workspace.video_registry import get_workspace
from .workspace.workspace_service import create_comparison_workspace
from .youtube_service import analyze_youtube_video


app = FastAPI(title=settings.app_name)


def _analyze_video_url(url: str) -> VideoAnalysisResponse:
    if "youtube.com" in url or "youtu.be" in url:
        video = analyze_youtube_video(url)
    elif "instagram.com" in url:
        video = analyze_instagram_reel(url)
    else:
        raise ValueError("Unsupported video URL. Use a YouTube URL or Instagram Reel URL.")

    video.rag_ingestion = ingest_video_transcript(video)
    return video


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


@app.post("/api/workspace/create", response_model=WorkspaceResponse)
def create_workspace_endpoint(request: WorkspaceRequest) -> WorkspaceResponse:
    try:
        video_a = _analyze_video_url(request.video_a_url)
        video_b = _analyze_video_url(request.video_b_url)
        workspace = create_comparison_workspace(
            video_a.model_dump(),
            video_b.model_dump(),
        )
        return WorkspaceResponse(**workspace)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/api/workspace/{workspace_id}")
def get_workspace_endpoint(workspace_id: str) -> dict:
    workspace = get_workspace(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")

    return {
        "workspace_id": workspace_id,
        **workspace,
    }
