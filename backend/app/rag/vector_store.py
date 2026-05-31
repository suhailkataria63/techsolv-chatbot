from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from .embeddings import get_embedding_model, get_embedding_setup_error


COLLECTION_NAME = "social_videos"
CHROMA_DIR = Path(__file__).resolve().parents[2] / "storage" / "chroma"


def get_vector_store() -> Chroma:
    embedding_model = get_embedding_model()
    if embedding_model is None:
        raise ValueError(get_embedding_setup_error())

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=str(CHROMA_DIR),
    )


def add_chunks_to_store(documents: list[Document]) -> int:
    if not documents:
        return 0

    store = get_vector_store()
    store.add_documents(documents)

    return len(documents)
