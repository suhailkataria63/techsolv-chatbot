import re
from pathlib import Path
from urllib.parse import urlparse

from yt_dlp import YoutubeDL

from .config import settings
from .models import VideoAnalysisResponse
from .video_metrics import calculate_engagement_rate, normalize_duration_seconds


def extract_instagram_shortcode(url: str) -> str:
    parsed_url = urlparse(url)
    path_parts = [part for part in parsed_url.path.split("/") if part]

    for marker in ("reel", "reels", "p", "tv"):
        if marker in path_parts:
            marker_index = path_parts.index(marker)
            if len(path_parts) > marker_index + 1:
                return path_parts[marker_index + 1]

    raise ValueError("Could not find an Instagram shortcode in the URL.")


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


def _instagram_ydl_options() -> dict:
    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }

    if settings.instagram_cookies_file:
        options["cookiefile"] = settings.instagram_cookies_file

    return options


def fetch_instagram_metadata(url: str) -> dict:
    try:
        with YoutubeDL(_instagram_ydl_options()) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as exc:
        raise ValueError(
            "Could not fetch Instagram metadata. Instagram may require cookies/auth, "
            "or the Reel may not be publicly accessible."
        ) from exc


def download_instagram_audio(url: str, output_dir: str = "storage/audio") -> str | None:
    try:
        shortcode = extract_instagram_shortcode(url)
        safe_shortcode = re.sub(r"[^A-Za-z0-9_-]", "_", shortcode)
        audio_dir = Path(output_dir)
        audio_dir.mkdir(parents=True, exist_ok=True)

        output_template = str(audio_dir / f"{safe_shortcode}.%(ext)s")
        options = _instagram_ydl_options()
        options.update(
            {
                "format": "bestaudio/best",
                "outtmpl": output_template,
                "skip_download": False,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                    }
                ],
            }
        )

        with YoutubeDL(options) as ydl:
            ydl.extract_info(url, download=True)

        audio_path = audio_dir / f"{safe_shortcode}.mp3"
        return str(audio_path) if audio_path.exists() else None
    except Exception:
        return None


def transcribe_audio_with_whisper(audio_path: str) -> tuple[str, str]:
    try:
        import whisper

        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        transcript = str(result.get("text", "")).strip()
        return transcript, "whisper" if transcript else "unavailable"
    except Exception:
        return "", "unavailable"


def analyze_instagram_reel(url: str) -> VideoAnalysisResponse:
    shortcode = extract_instagram_shortcode(url)
    metadata = fetch_instagram_metadata(url)

    title = metadata.get("title") or metadata.get("description")
    description = metadata.get("description")
    creator = metadata.get("uploader") or metadata.get("channel") or metadata.get("creator")
    views = metadata.get("view_count")
    likes = metadata.get("like_count")
    comments = metadata.get("comment_count")
    upload_date = _normalize_upload_date(metadata.get("upload_date"))
    duration_seconds = normalize_duration_seconds(metadata.get("duration"))

    audio_path = download_instagram_audio(url)
    if audio_path:
        transcript, transcript_source = transcribe_audio_with_whisper(audio_path)
    else:
        transcript, transcript_source = "", "unavailable"

    return VideoAnalysisResponse(
        video_id=metadata.get("id") or shortcode,
        platform="instagram",
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
