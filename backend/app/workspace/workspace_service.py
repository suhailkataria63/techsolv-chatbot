from uuid import uuid4

from .video_registry import WORKSPACES, create_workspace, save_video_a, save_video_b


def create_comparison_workspace(video_a, video_b) -> dict:
    workspace_id = str(uuid4())
    WORKSPACES[workspace_id] = create_workspace()

    save_video_a(workspace_id, video_a)
    save_video_b(workspace_id, video_b)

    return {
        "workspace_id": workspace_id,
        "video_a": video_a,
        "video_b": video_b,
    }
