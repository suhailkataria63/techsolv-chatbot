from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from ..config import settings


def get_embedding_model():
    provider = settings.embedding_provider.lower()

    if provider == "huggingface":
        return HuggingFaceEmbeddings(model_name=settings.embedding_model)

    if provider == "gemini":
        if not settings.google_api_key:
            return None

        return GoogleGenerativeAIEmbeddings(
            model=settings.gemini_embedding_model,
            google_api_key=settings.google_api_key,
        )

    if provider == "openai":
        if not settings.openai_api_key:
            return None

        return OpenAIEmbeddings(model="text-embedding-3-small")

    return None


def get_embedding_setup_error() -> str:
    provider = settings.embedding_provider.lower()

    if provider == "gemini" and not settings.google_api_key:
        return "GOOGLE_API_KEY is required for Gemini mode."

    if provider == "openai" and not settings.openai_api_key:
        return "OPENAI_API_KEY is required for OpenAI embedding mode."

    if provider not in {"huggingface", "gemini", "openai"}:
        return f"Unsupported EMBEDDING_PROVIDER: {settings.embedding_provider}"

    return f"Embedding provider {settings.embedding_provider} is unavailable."
