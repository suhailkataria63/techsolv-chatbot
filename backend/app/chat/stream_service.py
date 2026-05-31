import os

from langchain_openai import ChatOpenAI

from .chat_service import _format_context, _format_history
from .memory import add_message, get_recent_history
from .retriever import retrieve_relevant_chunks


NO_CONTEXT_STREAM_MESSAGE = (
    "I do not have transcript chunks to search yet. Analyze videos first, then ask again."
)

NO_KEY_STREAM_MESSAGE = (
    "Chat streaming needs OPENAI_API_KEY because retrieval and LLM response generation "
    "depend on embeddings/chat model."
)


def stream_answer(session_id: str, message: str):
    try:
        history = get_recent_history(session_id)
        chunks = retrieve_relevant_chunks(message)

        if not chunks:
            yield NO_CONTEXT_STREAM_MESSAGE
            add_message(session_id, "user", message)
            add_message(session_id, "assistant", NO_CONTEXT_STREAM_MESSAGE)
            return

        if not os.getenv("OPENAI_API_KEY"):
            yield NO_KEY_STREAM_MESSAGE
            add_message(session_id, "user", message)
            add_message(session_id, "assistant", NO_KEY_STREAM_MESSAGE)
            return

        prompt = f"""
You are answering questions about social video transcripts.

Use only the retrieved transcript context below. If the context does not contain
the answer, say that the available transcript chunks do not answer the question.
When you use a source, cite it inline using its Source value, such as [video_id#0].

Recent conversation:
{_format_history(history)}

Retrieved transcript context:
{_format_context(chunks)}

User question:
{message}
""".strip()

        model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, streaming=True)
        answer_parts = []

        for chunk in model.stream(prompt):
            token = chunk.content if isinstance(chunk.content, str) else str(chunk.content)
            if not token:
                continue

            answer_parts.append(token)
            yield token

        answer = "".join(answer_parts)
        add_message(session_id, "user", message)
        add_message(session_id, "assistant", answer)
    except Exception as exc:
        yield f"Could not stream chat response: {exc}"
