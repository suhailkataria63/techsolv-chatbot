import math


def _number(value) -> float:
    if value is None:
        return 0.0

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _log_points(value, scale: float, cap: float) -> float:
    value = _number(value)
    if value <= 0:
        return 0.0

    return min(math.log10(value + 1) * scale, cap)


def calculate_video_score(video) -> dict:
    engagement_rate = _number(video.get("engagement_rate"))
    likes = _number(video.get("likes"))
    comments = _number(video.get("comments"))
    views = _number(video.get("views"))
    hashtags = video.get("hashtags") or []
    transcript = video.get("transcript") or ""

    factors = []

    engagement_points = min(engagement_rate * 8, 45)
    if engagement_points:
        factors.append(f"Engagement rate contributed {engagement_points:.1f} points.")

    like_points = _log_points(likes, scale=3.0, cap=15)
    if like_points:
        factors.append(f"Likes contributed {like_points:.1f} points.")

    comment_points = _log_points(comments, scale=3.5, cap=15)
    if comment_points:
        factors.append(f"Comments contributed {comment_points:.1f} points.")

    view_points = _log_points(views, scale=2.5, cap=15)
    if view_points:
        factors.append(f"Views contributed {view_points:.1f} points.")

    hashtag_points = min(len(hashtags) * 1.2, 5)
    if hashtag_points:
        factors.append(f"Hashtags contributed {hashtag_points:.1f} points.")

    transcript_points = min(len(transcript) / 1000, 5)
    if transcript_points:
        factors.append(f"Transcript depth contributed {transcript_points:.1f} points.")

    score = engagement_points + like_points + comment_points
    score += view_points + hashtag_points + transcript_points

    if not factors:
        factors.append("No usable scoring metrics were available.")

    return {
        "score": round(score, 2),
        "factors": factors,
    }
