import logging

from langchain_core.documents import Document

from ..models import RagIngestionStatus
from .chunker import split_transcript
from .vector_store import COLLECTION_NAME, add_chunks_to_store


logger = logging.getLogger(__name__)


def _ingestion_status(
    status: str,
    stored_chunks: int = 0,
    collection_name: str | None = None,
    error: str | None = None,
) -> RagIngestionStatus:
    return RagIngestionStatus(
        status=status,
        stored_chunks=stored_chunks,
        collection_name=collection_name,
        error=error,
    )


def ingest_video_transcript(video_response) -> RagIngestionStatus:
    if not video_response.transcript.strip():
        logger.warning(
            "Skipping RAG ingestion for %s:%s because transcript is unavailable.",
            video_response.platform,
            video_response.video_id,
        )
        return _ingestion_status(status="skipped", error="Transcript unavailable")

    chunks = split_transcript(video_response.transcript)
    if not chunks:
        logger.warning(
            "Skipping RAG ingestion for %s:%s because transcript produced no chunks.",
            video_response.platform,
            video_response.video_id,
        )
        return _ingestion_status(status="skipped", error="Transcript unavailable")

    documents = []

    for index, chunk in enumerate(chunks):
        documents.append(
            Document(
                page_content=chunk,
                metadata={
                    "video_id": video_response.video_id,
                    "platform": video_response.platform,
                    "creator": video_response.creator or "",
                    "chunk_index": index,
                    "source_url": video_response.url,
                },
            )
        )

    try:
        stored_chunks = add_chunks_to_store(documents)
    except Exception as exc:
        error = str(exc) or "Vector ingestion failed"
        logger.warning(
            "RAG ingestion failed for %s:%s: %s",
            video_response.platform,
            video_response.video_id,
            error,
        )
        return _ingestion_status(status="failed", error=error)

    logger.info(
        "RAG ingestion stored %s chunks for %s:%s.",
        stored_chunks,
        video_response.platform,
        video_response.video_id,
    )
    return _ingestion_status(
        status="success",
        stored_chunks=stored_chunks,
        collection_name=COLLECTION_NAME,
    )
