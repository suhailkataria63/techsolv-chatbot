import re
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL

from .models import VideoAnalysisResponse
from .video_metrics import calculate_engagement_rate


def extract_youtube_video_id(url: str) -> str:
    parsed_url = urlparse(url)
    host = parsed_url.netloc.lower().replace("www.", "")

    if host == "youtu.be":
        video_id = parsed_url.path.strip("/").split("/")[0]
    elif host.endswith("youtube.com"):
        if parsed_url.path == "/watch":
            video_id = parse_qs(parsed_url.query).get("v", [""])[0]
        elif parsed_url.path.startswith(("/shorts/", "/embed/")):
            path_parts = parsed_url.path.strip("/").split("/")
            video_id = path_parts[1] if len(path_parts) > 1 else ""
        else:
            video_id = ""
    else:
        video_id = ""

    if not video_id:
        raise ValueError("Could not find a YouTube video id in the URL.")

    return video_id


def extract_hashtags(text: str | None) -> list[str]:
    if not text:
        return []

    tags = re.findall(r"(?<!\w)#([\w-]+)", text)
    seen = set()
    clean_tags = []

    for tag in tags:
        normalized = f"#{tag}"
        key = normalized.lower()
        if key not in seen:
            seen.add(key)
            clean_tags.append(normalized)

    return clean_tags


def _normalize_upload_date(upload_date: str | None) -> str | None:
    if not upload_date or not re.fullmatch(r"\d{8}", upload_date):
        return upload_date

    return f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"


def fetch_youtube_metadata(url: str) -> dict:
    try:
        with YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True}) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as exc:
        raise ValueError(f"Could not fetch YouTube metadata: {exc}") from exc


def fetch_youtube_transcript(video_id: str) -> tuple[str, str]:
    try:
        segments = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join(segment.get("text", "").strip() for segment in segments)
        return transcript.strip(), "youtube-transcript-api"
    except AttributeError:
        try:
            fetched = YouTubeTranscriptApi().fetch(video_id)
            transcript = " ".join(snippet.text.strip() for snippet in fetched)
            return transcript.strip(), "youtube-transcript-api"
        except Exception:
            return "", "unavailable"
    except Exception:
        return "", "unavailable"


def analyze_youtube_video(url: str) -> VideoAnalysisResponse:
    video_id = extract_youtube_video_id(url)
    metadata = fetch_youtube_metadata(url)

    title = metadata.get("title")
    description = metadata.get("description")
    creator = metadata.get("uploader") or metadata.get("channel")
    views = metadata.get("view_count")
    likes = metadata.get("like_count")
    comments = metadata.get("comment_count")
    upload_date = _normalize_upload_date(metadata.get("upload_date"))
    duration_seconds = metadata.get("duration")
    transcript, transcript_source = fetch_youtube_transcript(video_id)

    return VideoAnalysisResponse(
        video_id=metadata.get("id") or video_id,
        platform="youtube",
        url=url,
        title=title,
        creator=creator,
        views=views,
        likes=likes,
        comments=comments,
        upload_date=upload_date,
        duration_seconds=duration_seconds,
        hashtags=extract_hashtags(f"{title or ''}\n{description or ''}"),
        engagement_rate=calculate_engagement_rate(likes, comments, views),
        transcript=transcript,
        transcript_source=transcript_source,
    )
