# Architecture notes

FastAPI is a good fit for the backend because the API surface will stay fairly small, and it gives us clean request handling, validation, and streaming support without much ceremony.

Next.js is planned for the frontend because it is a practical default for a chat-style web app. It can handle the initial form, streaming chat UI, and later deployment without forcing a separate frontend architecture decision too early.

LangChain will sit in the RAG layer so the project has a clear place for document loading, chunk retrieval, chat memory, and model calls. The goal is to use it where it helps, not to wrap every small function in a framework.

Chroma is planned for local development because it is simple to run locally and works well for testing transcript chunk storage and retrieval before adding managed infrastructure.

For production, the vector store could move to Qdrant, Pinecone, or Postgres with pgvector depending on hosting, cost, and operational needs.

Transcript extraction and metadata fetching should stay separate from the RAG logic. The extraction layer can deal with YouTube and Instagram quirks, while the RAG layer only needs normalized transcript chunks, metadata, and source references.

That separation also leaves room for Instagram fallbacks and future background jobs. If extraction gets slow or needs cookies/auth handling, it can move behind a queue without changing how retrieval and chat consume the cleaned video data.
