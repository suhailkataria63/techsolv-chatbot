import os

from langchain_openai import ChatOpenAI

from ..models import ChatResponse, Citation
from .memory import add_message, get_recent_history
from .retriever import retrieve_relevant_chunks


NO_CONTEXT_ANSWER = (
    "I do not have any transcript chunks to search yet. Analyze a YouTube video "
    "or Instagram Reel first, then ask again once ingestion has stored chunks."
)


def _format_history(history: list[dict]) -> str:
    if not history:
        return "No recent conversation."

    return "\n".join(
        f"{message['role']}: {message['content']}" for message in history
    )


def _format_context(chunks: list[dict]) -> str:
    lines = []
    for chunk in chunks:
        metadata = chunk["metadata"]
        citation_label = f"{metadata.get('video_id')}#{metadata.get('chunk_index')}"
        lines.append(
            "\n".join(
                [
                    f"Source: {citation_label}",
                    f"Platform: {metadata.get('platform')}",
                    f"Creator: {metadata.get('creator')}",
                    f"URL: {metadata.get('source_url')}",
                    f"Text: {chunk['content']}",
                ]
            )
        )

    return "\n\n".join(lines)


def _build_citations(chunks: list[dict]) -> list[Citation]:
    citations = []
    seen = set()

    for chunk in chunks:
        metadata = chunk["metadata"]
        key = (
            metadata.get("video_id"),
            metadata.get("platform"),
            metadata.get("chunk_index"),
            metadata.get("source_url"),
        )
        if key in seen:
            continue

        seen.add(key)
        citations.append(
            Citation(
                video_id=metadata.get("video_id"),
                platform=metadata.get("platform"),
                creator=metadata.get("creator"),
                chunk_index=metadata.get("chunk_index"),
                source_url=metadata.get("source_url"),
            )
        )

    return citations


def answer_question(session_id: str, message: str) -> ChatResponse:
    history = get_recent_history(session_id)
    chunks = retrieve_relevant_chunks(message)

    add_message(session_id, "user", message)

    if not chunks:
        add_message(session_id, "assistant", NO_CONTEXT_ANSWER)
        return ChatResponse(
            session_id=session_id,
            answer=NO_CONTEXT_ANSWER,
            citations=[],
        )

    if not os.getenv("OPENAI_API_KEY"):
        answer = (
            "I found transcript chunks, but chat generation needs OPENAI_API_KEY. "
            "Set it in the backend environment and try again."
        )
        add_message(session_id, "assistant", answer)
        return ChatResponse(
            session_id=session_id,
            answer=answer,
            citations=_build_citations(chunks),
        )

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

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    response = model.invoke(prompt)
    answer = response.content if isinstance(response.content, str) else str(response.content)

    add_message(session_id, "assistant", answer)

    return ChatResponse(
        session_id=session_id,
        answer=answer,
        citations=_build_citations(chunks),
    )
