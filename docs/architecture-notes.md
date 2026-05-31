# Architecture notes

FastAPI is a good fit for the backend because the API surface will stay fairly small, and it gives us clean request handling, validation, and streaming support without much ceremony.

Next.js is planned for the frontend because it is a practical default for a chat-style web app. It can handle the initial form, streaming chat UI, and later deployment without forcing a separate frontend architecture decision too early.

LangChain will sit in the RAG layer so the project has a clear place for document loading, chunk retrieval, chat memory, and model calls. The goal is to use it where it helps, not to wrap every small function in a framework.

Chroma is planned for local development because it is simple to run locally and works well for testing transcript chunk storage and retrieval before adding managed infrastructure.

For production, the vector store could move to Qdrant, Pinecone, or Postgres with pgvector depending on hosting, cost, and operational needs.

The first ingestion pass uses ChromaDB with a local persistent directory at `backend/storage/chroma`. That keeps setup light for a screening project while still proving that chunks, embeddings, and metadata survive process restarts.

Transcript chunking uses `RecursiveCharacterTextSplitter` with 700-character chunks and 120-character overlap. It is a plain starting point: small enough for precise retrieval, with enough overlap to keep sentences and short explanations from being split too harshly.

Embeddings use `text-embedding-3-small` because transcript chunks are short and cost matters during repeated testing. If retrieval quality becomes the bottleneck later, this can be swapped without changing the extraction layer.

AI providers are configurable so the project can run in different environments. HuggingFace embeddings plus Ollama chat are the default local path because they avoid per-call costs and keep development independent of hosted APIs. Gemini is useful for Loom/demo mode because it gives hosted model quality with less local setup. OpenAI remains available as an optional provider.

Embedding provider changes require rebuilding the vector store. Vectors from HuggingFace, Gemini, and OpenAI live in different embedding spaces, so `backend/storage/chroma` should be deleted and videos should be re-analyzed after switching providers.

Managed providers are still useful in production for latency, reliability, observability, and avoiding local model operations. The tradeoff is cost and external dependency risk, so provider errors are surfaced explicitly instead of being framed as generic OpenAI failures.

Retrieval is kept separate from answer generation so each piece can fail or change independently. The retriever only knows how to find relevant chunks; the chat service decides how to use those chunks, recent memory, and the model response.

Citations come directly from chunk metadata written during ingestion. That keeps citations tied to stored transcript chunks instead of asking the model to invent source references.

Semantic search alone is weak for UI labels such as `Video A`, `Video B`, or a creator name that may only exist in metadata. Metadata-aware retrieval resolves those labels to the workspace video ids first, then filters Chroma by `video_id` before searching. Summary questions use broader ordered chunk retrieval because a good summary needs coverage across the transcript, not just the single most semantically similar chunk.

Workspace metadata is included in the chat prompt alongside retrieved chunks. Transcripts answer "what was said"; metadata answers "who posted it", "when was it uploaded", "how many views/likes/comments it has", and "how well it performed". That split improves creator, engagement, and Video A/B questions without asking the model to infer metadata from transcript text.

Chat memory is in-memory for now because it is enough to prove session behavior in local development. A production version should move this to Redis or Postgres so history survives restarts, can expire cleanly, and can be shared across workers.

Streaming chat improves perceived latency because the user sees the answer as it is generated instead of waiting for the full response. The non-streaming endpoint is still useful for debugging, tests, and clients that want structured citations in the same response body.

For streaming, memory is updated after the stream completes. That avoids storing partial assistant messages if generation is interrupted halfway through.

The comparison workspace exists so the app can treat Video A and Video B as a pair after extraction. Comparison workflows should not repeatedly re-fetch the same URLs just to render metadata, calculate differences, or build follow-up prompts.

Workspace storage is in-memory for now, matching the current chat memory approach. A production version should move workspaces into Postgres or another durable store, especially if users need to return to a comparison later or share it.

The comparison engine is deterministic for now. Engagement rate is weighted most heavily because it normalizes interaction against reach, while likes, comments, and views provide medium-strength popularity signals. Hashtag count and transcript length are minor signals because they can help explain discoverability and content depth, but they should not overpower actual audience response.

Missing metrics are treated as zero contribution rather than errors. That matters for Instagram because public extraction can return partial metadata depending on access, cookies, and platform behavior.

At larger scale, ingestion should move out of the request cycle into a background job. The API can return an accepted analysis result, then a queue worker can chunk, embed, retry failures, and write to a managed vector store.

The ingestion path is deliberately non-blocking from the user's point of view. External AI providers, local vector stores, and API keys are all failure points, so the app should keep metadata/transcript extraction useful even when embeddings are down.

Resilient AI pipelines matter because each step depends on a different external system: social platforms can block extraction, OpenAI can reject embedding requests, and local storage can be unavailable. Keeping those failures isolated makes debugging clearer and avoids turning a partial success into a blank response.

In production, failed ingestion should be retryable through a job queue with status tracking. A user-uploaded transcript/audio fallback, provider failover, and managed vector storage would reduce the chance that one dependency blocks the whole workflow.

Transcript extraction and metadata fetching should stay separate from the RAG logic. The extraction layer can deal with YouTube and Instagram quirks, while the RAG layer only needs normalized transcript chunks, metadata, and source references.

That separation also leaves room for Instagram fallbacks and future background jobs. If extraction gets slow or needs cookies/auth handling, it can move behind a queue without changing how retrieval and chat consume the cleaned video data.

Instagram extraction is intentionally isolated because it is the least stable external integration in this project. A production version should prefer creator OAuth, official APIs where possible, approved data providers, or a user-uploaded video/audio fallback. Whisper is useful as a fallback transcript path, but it adds compute cost and should not be treated like a free metadata field.
