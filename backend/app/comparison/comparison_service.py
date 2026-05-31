from .scoring import calculate_video_score


def _number(video: dict, key: str) -> float:
    value = video.get(key)
    if value is None:
        return 0.0

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _count_hashtags(video: dict) -> int:
    return len(video.get("hashtags") or [])


def _transcript_size(video: dict) -> int:
    return len(video.get("transcript") or "")


def _title(video: dict, fallback: str) -> str:
    return video.get("title") or video.get("creator") or fallback


def _better(metric_name: str, video_a: dict, video_b: dict) -> str | None:
    value_a = _number(video_a, metric_name)
    value_b = _number(video_b, metric_name)

    if value_a > value_b:
        return "video_a"
    if value_b > value_a:
        return "video_b"
    return None


def _strengths(video: dict, other: dict, label: str) -> list[str]:
    strengths = []

    for key, name in (
        ("engagement_rate", "higher engagement rate"),
        ("views", "more views"),
        ("likes", "more likes"),
        ("comments", "more comments"),
    ):
        if _number(video, key) > _number(other, key):
            strengths.append(f"{label} has {name}.")

    if _count_hashtags(video) > _count_hashtags(other):
        strengths.append(f"{label} uses more hashtags.")

    if _transcript_size(video) > _transcript_size(other):
        strengths.append(f"{label} has more transcript content available.")

    duration = _number(video, "duration_seconds")
    other_duration = _number(other, "duration_seconds")
    if duration and other_duration and duration < other_duration:
        strengths.append(f"{label} is shorter, which may help completion rate.")

    if not strengths:
        strengths.append(f"{label} does not clearly lead on the available metrics.")

    return strengths


def _suggestions(video_a: dict, video_b: dict, winner: str) -> list[str]:
    suggestions = []

    if winner == "tie":
        return [
            "Scores are tied on the available data. Compare hooks, pacing, and audience prompts manually.",
            "Collect more complete metrics if either platform returned missing values.",
        ]

    weaker = video_b if winner == "video_a" else video_a
    weaker_label = "Video B" if winner == "video_a" else "Video A"

    if not weaker.get("engagement_rate"):
        suggestions.append(f"{weaker_label} needs better engagement data or stronger audience response.")

    if not weaker.get("comments"):
        suggestions.append(f"{weaker_label} could add a clearer prompt for comments or discussion.")

    if _count_hashtags(weaker) < 3:
        suggestions.append(f"{weaker_label} could test a few more relevant hashtags.")

    if _transcript_size(weaker) < 300:
        suggestions.append(f"{weaker_label} may need clearer spoken content or captions for richer analysis.")

    if not suggestions:
        suggestions.append("Review the stronger video's hook, pacing, and audience prompt, then test those patterns.")

    return suggestions


def compare_workspace(workspace: dict) -> dict:
    video_a = workspace["video_a"]
    video_b = workspace["video_b"]
    score_a = calculate_video_score(video_a)
    score_b = calculate_video_score(video_b)

    if score_a["score"] > score_b["score"]:
        winner = "video_a"
    elif score_b["score"] > score_a["score"]:
        winner = "video_b"
    else:
        winner = "tie"

    metric_winners = {
        "duration": _better("duration_seconds", video_a, video_b),
        "views": _better("views", video_a, video_b),
        "likes": _better("likes", video_a, video_b),
        "comments": _better("comments", video_a, video_b),
        "engagement": _better("engagement_rate", video_a, video_b),
        "hashtags": (
            "video_a"
            if _count_hashtags(video_a) > _count_hashtags(video_b)
            else "video_b"
            if _count_hashtags(video_b) > _count_hashtags(video_a)
            else None
        ),
        "transcript_size": (
            "video_a"
            if _transcript_size(video_a) > _transcript_size(video_b)
            else "video_b"
            if _transcript_size(video_b) > _transcript_size(video_a)
            else None
        ),
    }

    summary = (
        f"{_title(video_a, 'Video A')} scored {score_a['score']}, while "
        f"{_title(video_b, 'Video B')} scored {score_b['score']}. "
        f"The winner is {winner.replace('_', ' ')} based on engagement, reach, "
        "conversation signals, hashtag usage, and transcript depth."
    )

    return {
        "winner": winner,
        "score_a": score_a["score"],
        "score_b": score_b["score"],
        "comparison_summary": summary,
        "strengths_video_a": _strengths(video_a, video_b, "Video A"),
        "strengths_video_b": _strengths(video_b, video_a, "Video B"),
        "improvement_suggestions": _suggestions(video_a, video_b, winner),
        "metric_winners": metric_winners,
        "score_factors": {
            "video_a": score_a["factors"],
            "video_b": score_b["factors"],
        },
    }
