from datetime import datetime, timezone


WORKSPACES = {}


def create_workspace() -> dict:
    return {
        "video_a": None,
        "video_b": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def get_workspace(workspace_id):
    return WORKSPACES.get(workspace_id)


def save_video_a(workspace_id, video_data) -> None:
    WORKSPACES[workspace_id]["video_a"] = video_data


def save_video_b(workspace_id, video_data) -> None:
    WORKSPACES[workspace_id]["video_b"] = video_data
