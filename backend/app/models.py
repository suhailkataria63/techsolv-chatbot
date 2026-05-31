from typing import Literal

from pydantic import BaseModel


class VideoUrlRequest(BaseModel):
    url: str


class ChatRequest(BaseModel):
    session_id: str
    message: str


class Citation(BaseModel):
    video_id: str | None
    platform: str | None
    creator: str | None
    chunk_index: int | None
    source_url: str | None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    citations: list[Citation]


class RagIngestionStatus(BaseModel):
    status: Literal["success", "failed", "skipped"]
    stored_chunks: int
    collection_name: str | None
    error: str | None


class VideoAnalysisResponse(BaseModel):
    video_id: str
    platform: str
    url: str
    title: str | None
    creator: str | None
    views: int | None
    likes: int | None
    comments: int | None
    upload_date: str | None
    duration_seconds: int | None
    hashtags: list[str]
    engagement_rate: float | None
    transcript: str
    transcript_source: str
    rag_ingestion: RagIngestionStatus | None = None
