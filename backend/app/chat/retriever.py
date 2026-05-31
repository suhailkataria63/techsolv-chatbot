import logging
import re

from ..rag.vector_store import get_vector_store


logger = logging.getLogger(__name__)


def normalize_question_for_search(question: str) -> str:
    cleaned = question
    replacements = [
        r"\bvideo\s*a\b",
        r"\bvideo\s*b\b",
        r"\bfirst\s+video\b",
        r"\bsecond\s+video\b",
        r"\byoutube\s+video\b",
        r"\binstagram\s+video\b",
        r"\breel\b",
        r"\bcreator\b",
        r"\bspeaker\b",
        r"\bvideo\b",
    ]

    for pattern in replacements:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or question


def detect_video_reference(question: str) -> str | None:
    normalized = question.lower()

    if re.search(r"\b(video\s*a|first\s+video|youtube\s+video)\b", normalized):
        return "video_a"

    if re.search(r"\b(video\s*b|second\s+video|instagram\s+video|reel)\b", normalized):
        return "video_b"

    return None


def _document_to_chunk(document) -> dict:
    return {
        "content": document.page_content,
        "metadata": {
            "video_id": document.metadata.get("video_id"),
            "platform": document.metadata.get("platform"),
            "creator": document.metadata.get("creator"),
            "chunk_index": document.metadata.get("chunk_index"),
            "source_url": document.metadata.get("source_url"),
        },
    }


def _stored_item_to_chunk(content: str, metadata: dict) -> dict:
    return {
        "content": content,
        "metadata": {
            "video_id": metadata.get("video_id"),
            "platform": metadata.get("platform"),
            "creator": metadata.get("creator"),
            "chunk_index": metadata.get("chunk_index"),
            "source_url": metadata.get("source_url"),
        },
    }


def retrieve_chunks_by_video_id(video_id: str, k: int = 12) -> list[dict]:
    try:
        store = get_vector_store()
        result = store.get(where={"video_id": video_id})
    except Exception as exc:
        logger.warning("Video-specific retrieval skipped for %s: %s", video_id, exc)
        return []

    documents = result.get("documents") or []
    metadatas = result.get("metadatas") or []
    chunks = [
        _stored_item_to_chunk(content, metadata or {})
        for content, metadata in zip(documents, metadatas)
    ]

    chunks.sort(key=lambda chunk: chunk["metadata"].get("chunk_index") or 0)
    return chunks[:k]


def retrieve_chunks_by_video_label(
    video_label: str,
    workspace: dict | None = None,
    k: int = 12,
) -> list[dict]:
    if not workspace:
        return []

    video = workspace.get(video_label) or {}
    video_id = video.get("video_id")
    if not video_id:
        return []

    return retrieve_chunks_by_video_id(video_id, k=k)


def retrieve_relevant_chunks(
    query: str,
    k: int = 8,
    video_id: str | None = None,
) -> list[dict]:
    search_query = normalize_question_for_search(query)

    try:
        store = get_vector_store()
        if video_id:
            documents = store.similarity_search(
                search_query,
                k=k,
                filter={"video_id": video_id},
            )
        else:
            documents = store.similarity_search(search_query, k=k)
    except Exception as exc:
        logger.warning("Chunk retrieval skipped: %s", exc)
        return []

    return [_document_to_chunk(document) for document in documents]
