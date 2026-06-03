from .chat_service import (
    INSUFFICIENT_CONTEXT_ANSWER,
    build_grounded_prompt,
    get_chat_context,
    get_chat_model,
    get_llm_setup_error,
    provider_runtime_error,
)
from .memory import add_message, get_recent_history


NO_CONTEXT_STREAM_MESSAGE = (
    "I do not have transcript chunks to search yet. Analyze videos first, then ask again."
)


def stream_answer(session_id: str, message: str):
    try:
        history = get_recent_history(session_id)
        setup_error = get_llm_setup_error()

        if setup_error:
            yield setup_error
            add_message(session_id, "user", message)
            add_message(session_id, "assistant", setup_error)
            return

        workspace, chunks, summary_mode, position_mode = get_chat_context(
            session_id,
            message,
        )

        if summary_mode and not chunks:
            yield INSUFFICIENT_CONTEXT_ANSWER
            add_message(session_id, "user", message)
            add_message(session_id, "assistant", INSUFFICIENT_CONTEXT_ANSWER)
            return

        if not chunks and not workspace:
            yield NO_CONTEXT_STREAM_MESSAGE
            add_message(session_id, "user", message)
            add_message(session_id, "assistant", NO_CONTEXT_STREAM_MESSAGE)
            return

        prompt = build_grounded_prompt(
            history,
            chunks,
            message,
            workspace,
            summary_mode=summary_mode,
            position_mode=position_mode,
        )

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
