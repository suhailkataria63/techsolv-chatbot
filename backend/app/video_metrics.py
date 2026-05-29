def calculate_engagement_rate(
    likes: int | None,
    comments: int | None,
    views: int | None,
) -> float | None:
    if not views:
        return None

    total_engagements = (likes or 0) + (comments or 0)
    return round((total_engagements / views) * 100, 2)
