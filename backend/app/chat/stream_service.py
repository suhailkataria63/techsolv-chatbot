from .chat_service import (
    build_grounded_prompt,
    get_chunks_for_message,
    get_chat_model,
    get_llm_setup_error,
    provider_runtime_error,
)
from .memory import add_message, get_recent_history
from ..workspace.video_registry import get_workspace


NO_CONTEXT_STREAM_MESSAGE = (
    "I do not have transcript chunks to search yet. Analyze videos first, then ask again."
)


def stream_answer(session_id: str, message: str):
    try:
        history = get_recent_history(session_id)
        stored_workspace = get_workspace(session_id)
        workspace = (
            {
                "workspace_id": session_id,
                **stored_workspace,
            }
            if stored_workspace
            else None
        )
        setup_error = get_llm_setup_error()

        if setup_error:
            yield setup_error
            add_message(session_id, "user", message)
            add_message(session_id, "assistant", setup_error)
            return

        chunks = get_chunks_for_message(session_id, message)

        if not chunks and not workspace:
            yield NO_CONTEXT_STREAM_MESSAGE
            add_message(session_id, "user", message)
            add_message(session_id, "assistant", NO_CONTEXT_STREAM_MESSAGE)
            return

        prompt = build_grounded_prompt(history, chunks, message, workspace)

        model = get_chat_model(streaming=True)
        if model is None:
            error = get_llm_setup_error() or "Chat model is unavailable."
            yield error
            add_message(session_id, "user", message)
            add_message(session_id, "assistant", error)
            return

        answer_parts = []

        try:
            for chunk in model.stream(prompt):
                token = chunk.content if isinstance(chunk.content, str) else str(chunk.content)
                if not token:
                    continue

                answer_parts.append(token)
                yield token
        except Exception as exc:
            error = provider_runtime_error(exc)
            yield error
            add_message(session_id, "user", message)
            add_message(session_id, "assistant", error)
            return

        answer = "".join(answer_parts)
        add_message(session_id, "user", message)
        add_message(session_id, "assistant", answer)
    except Exception as exc:
        yield f"Could not stream chat response: {exc}"
