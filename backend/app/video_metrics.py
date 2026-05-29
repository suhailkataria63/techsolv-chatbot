def calculate_engagement_rate(
    likes: int | None,
    comments: int | None,
    views: int | None,
) -> float | None:
    if not views:
        return None

    total_engagements = (likes or 0) + (comments or 0)
    return round((total_engagements / views) * 100, 2)


def normalize_duration_seconds(value) -> int | None:
    if value is None:
        return None

    if isinstance(value, int):
        return value

    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None
