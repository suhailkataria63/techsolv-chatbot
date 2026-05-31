import logging

from ..rag.vector_store import get_vector_store


logger = logging.getLogger(__name__)


def retrieve_relevant_chunks(query: str, k: int = 5) -> list[dict]:
    try:
        store = get_vector_store()
        documents = store.similarity_search(query, k=k)
    except Exception as exc:
        logger.warning("Chunk retrieval skipped: %s", exc)
        return []

    chunks = []
    for document in documents:
        chunks.append(
            {
                "content": document.page_content,
                "metadata": {
                    "video_id": document.metadata.get("video_id"),
                    "platform": document.metadata.get("platform"),
                    "creator": document.metadata.get("creator"),
                    "chunk_index": document.metadata.get("chunk_index"),
                    "source_url": document.metadata.get("source_url"),
                },
            }
        )

    return chunks
