from pydantic import BaseModel


class VideoUrlRequest(BaseModel):
    url: str


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
