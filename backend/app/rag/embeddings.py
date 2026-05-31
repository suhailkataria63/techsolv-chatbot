import os

from langchain_openai import OpenAIEmbeddings


def get_embedding_model() -> OpenAIEmbeddings | None:
    if not os.getenv("OPENAI_API_KEY"):
        return None

    return OpenAIEmbeddings(model="text-embedding-3-small")
