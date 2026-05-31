import re

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from ..config import settings
from ..models import ChatResponse, Citation
from ..workspace.video_registry import get_workspace
from .memory import add_message, get_recent_history
from .retriever import (
    detect_video_reference,
    retrieve_chunks_by_video_label,
    retrieve_relevant_chunks,
)


NO_CONTEXT_ANSWER = (
    "I do not have any transcript chunks to search yet. Analyze a YouTube video "
    "or Instagram Reel first, then ask again once ingestion has stored chunks."
)


def get_llm_setup_error() -> str | None:
    provider = settings.llm_provider.lower()

    if provider == "gemini" and not settings.google_api_key:
        return "GOOGLE_API_KEY is required for Gemini mode."

    if provider == "openai" and not settings.openai_api_key:
        return "OPENAI_API_KEY is required for OpenAI chat mode."

    if provider not in {"ollama", "gemini", "openai"}:
        return f"Unsupported LLM_PROVIDER: {settings.llm_provider}"

    return None


def get_chat_model(streaming: bool = False):
    provider = settings.llm_provider.lower()

    if provider == "ollama":
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.2,
        )

    if provider == "gemini":
        if not settings.google_api_key:
            return None

        return ChatGoogleGenerativeAI(
            model=settings.gemini_llm_model,
            google_api_key=settings.google_api_key,
            temperature=0.2,
            streaming=streaming,
        )

    if provider == "openai":
        if not settings.openai_api_key:
            return None

        return ChatOpenAI(model="gpt-4o-mini", temperature=0.2, streaming=streaming)

    return None


def provider_runtime_error(exc: Exception) -> str:
    provider = settings.llm_provider.lower()

    if provider == "ollama":
        return "Local Ollama model is unavailable. Start Ollama or switch LLM_PROVIDER."

    if provider == "gemini":
        return "Gemini chat request failed. Check GOOGLE_API_KEY and Gemini model settings."

    if provider == "openai":
        return "OpenAI chat request failed. Check OPENAI_API_KEY or switch LLM_PROVIDER."

    return str(exc) or "Chat model request failed."


def _format_history(history: list[dict]) -> str:
    if not history:
        return "No recent conversation."

    return "\n".join(
        f"{message['role']}: {message['content']}" for message in history
    )


def _format_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No retrieved transcript chunks."

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


def _format_value(value) -> str:
    if value is None or value == "":
        return "unknown"

    return str(value)


def _format_video_metadata(label: str, video: dict | None) -> str:
    if not video:
        return f"{label}: unavailable"

    rag_ingestion = video.get("rag_ingestion") or {}
    lines = [
        f"{label}:",
        f"- video_id: {_format_value(video.get('video_id'))}",
        f"- platform: {_format_value(video.get('platform'))}",
        f"- title: {_format_value(video.get('title'))}",
        f"- creator: {_format_value(video.get('creator'))}",
        f"- views: {_format_value(video.get('views'))}",
        f"- likes: {_format_value(video.get('likes'))}",
        f"- comments: {_format_value(video.get('comments'))}",
        f"- engagement_rate: {_format_value(video.get('engagement_rate'))}",
        f"- upload_date: {_format_value(video.get('upload_date'))}",
        f"- duration_seconds: {_format_value(video.get('duration_seconds'))}",
        f"- transcript_source: {_format_value(video.get('transcript_source'))}",
        f"- rag_ingestion_status: {_format_value(rag_ingestion.get('status'))}",
        f"- rag_stored_chunks: {_format_value(rag_ingestion.get('stored_chunks'))}",
    ]
    return "\n".join(lines)


def format_workspace_metadata(workspace: dict | None) -> str:
    if not workspace:
        return "No workspace metadata available."

    return "\n\n".join(
        [
            f"workspace_id: {_format_value(workspace.get('workspace_id'))}",
            _format_video_metadata("Video A", workspace.get("video_a")),
            _format_video_metadata("Video B", workspace.get("video_b")),
        ]
    )


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


def _is_summary_question(message: str) -> bool:
    normalized = message.lower()
    summary_terms = (
        "summarize",
        "summary",
        "main topic",
        "key points",
        "what is video a about",
        "what is video b about",
    )
    return any(term in normalized for term in summary_terms)


def _is_compare_question(message: str) -> bool:
    normalized = message.lower()
    return "compare" in normalized and ("video a" in normalized or "video b" in normalized)


def _video_id_for_label(video_label: str, workspace: dict | None) -> str | None:
    if not workspace:
        return None

    video = workspace.get(video_label) or {}
    return video.get("video_id")


def _video_id_for_metadata_match(message: str, workspace: dict | None) -> str | None:
    if not workspace:
        return None

    normalized = message.lower()
    for label in ("video_a", "video_b"):
        video = workspace.get(label) or {}
        creator = (video.get("creator") or "").strip()
        title = (video.get("title") or "").strip()

        if creator and creator.lower() in normalized:
            return video.get("video_id")

        title_words = [
            word
            for word in re.split(r"[^A-Za-z0-9]+", title)
            if len(word) >= 4
        ]
        title_matches = sum(1 for word in title_words if word.lower() in normalized)
        if title_matches >= 2:
            return video.get("video_id")

    return None


def get_chunks_for_message(session_id: str, message: str) -> list[dict]:
    workspace = get_workspace(session_id)
    video_label = detect_video_reference(message)

    if _is_compare_question(message) and workspace:
        chunks = []
        chunks.extend(retrieve_chunks_by_video_label("video_a", workspace, k=8))
        chunks.extend(retrieve_chunks_by_video_label("video_b", workspace, k=8))
        return chunks

    if video_label:
        if _is_summary_question(message):
            return retrieve_chunks_by_video_label(video_label, workspace, k=12)

        video_id = _video_id_for_label(video_label, workspace)
        if video_id:
            return retrieve_relevant_chunks(message, k=8, video_id=video_id)

    metadata_video_id = _video_id_for_metadata_match(message, workspace)
    if metadata_video_id:
        return retrieve_relevant_chunks(message, k=8, video_id=metadata_video_id)

    return retrieve_relevant_chunks(message, k=8)


def build_grounded_prompt(
    history: list[dict],
    chunks: list[dict],
    message: str,
    workspace: dict | None = None,
) -> str:
    return f"""
You are answering questions about analyzed social videos.

Use workspace metadata for identity, platform, creator, title, timing, transcript availability, and performance metrics such as views, likes, comments, and engagement rate.

Use retrieved transcript chunks for spoken content. If the user asks what was said, answer from transcript chunks. If the user asks about creator/title identity or performance metrics, workspace metadata is valid context.

If a video has few or zero stored transcript chunks, say that transcript context is limited instead of saying there is no information about the video when metadata is available.

Do not reject an answer only because the speaker name, title, or UI label is missing from the transcript if workspace metadata clearly links the question to the relevant video. If the transcript chunks truly do not contain the spoken topic, say that the transcript does not include enough detail.

Do not invent facts. Cite transcript sources inline using their Source value, such as [video_id#0], when using transcript chunks.

Recent conversation:
{_format_history(history)}

Workspace metadata:
{format_workspace_metadata(workspace)}

Retrieved transcript context:
{_format_context(chunks)}

User question:
{message}
""".strip()


def answer_question(session_id: str, message: str) -> ChatResponse:
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
        add_message(session_id, "user", message)
        add_message(session_id, "assistant", setup_error)
        return ChatResponse(
            session_id=session_id,
            answer=setup_error,
            citations=[],
        )

    chunks = get_chunks_for_message(session_id, message)

    add_message(session_id, "user", message)

    if not chunks and not workspace:
        add_message(session_id, "assistant", NO_CONTEXT_ANSWER)
        return ChatResponse(
            session_id=session_id,
            answer=NO_CONTEXT_ANSWER,
            citations=[],
        )

    prompt = build_grounded_prompt(history, chunks, message, workspace)

    model = get_chat_model()
    if model is None:
        answer = get_llm_setup_error() or "Chat model is unavailable."
    else:
        try:
            response = model.invoke(prompt)
            answer = response.content if isinstance(response.content, str) else str(response.content)
        except Exception as exc:
            answer = provider_runtime_error(exc)

    add_message(session_id, "assistant", answer)

    return ChatResponse(
        session_id=session_id,
        answer=answer,
        citations=_build_citations(chunks),
    )
