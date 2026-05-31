chat_histories: dict[str, list[dict]] = {}


def get_history(session_id: str) -> list[dict]:
    return chat_histories.get(session_id, [])


def add_message(session_id: str, role: str, content: str) -> None:
    chat_histories.setdefault(session_id, []).append(
        {
            "role": role,
            "content": content,
        }
    )


def get_recent_history(session_id: str, limit: int = 6) -> list[dict]:
    return get_history(session_id)[-limit:]
