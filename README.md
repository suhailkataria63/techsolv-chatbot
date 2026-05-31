# Social Video RAG Chatbot

A full-stack app for asking questions about short social videos.

The finished version will accept one YouTube URL and one Instagram Reel URL, pull transcript and metadata where available, calculate engagement rate, store transcript chunks in a vector database, and provide a streaming LangChain-based chat interface with citations and conversation memory.

## Current status

Phase 5 retrieval chat. The repo has a small FastAPI backend with health checks, YouTube analysis, Instagram Reel analysis, transcript ingestion into Chroma, and a basic RAG chat endpoint with citations. The frontend is still intentionally left out.

## Planned stack

- FastAPI for the backend API
- Next.js for the frontend
- LangChain for the RAG chat flow
- Chroma for local vector storage
- OpenAI for embeddings and chat responses
- yt-dlp for YouTube metadata
- youtube-transcript-api for YouTube transcripts
- yt-dlp for Instagram metadata where public access works
- Whisper for Instagram transcript fallback
- LangChain for transcript chunking and ingestion
- ChromaDB for local persistent vector storage

## Local backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Then check:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "social-video-rag-api"
}
```

## Local frontend setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

The backend runs on `http://127.0.0.1:8000`. The frontend usually runs on `http://localhost:3000`, but Next.js may use `3001` if `3000` is busy. CORS is enabled for local development on both `localhost` and `127.0.0.1` for ports `3000` and `3001`.

The frontend expects the backend at `NEXT_PUBLIC_API_BASE_URL`, which defaults to `http://127.0.0.1:8000`.

For local development, run the backend and frontend in separate terminals:

```bash
cd backend
uvicorn app.main:app --reload
```

```bash
cd frontend
npm run dev
```

## AI provider setup

The backend can run without OpenAI. Pick one mode in `backend/.env`.

Local free mode uses HuggingFace embeddings and Ollama chat:

```bash
EMBEDDING_PROVIDER=huggingface
LLM_PROVIDER=ollama
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434
```

Make sure Ollama is running locally and the model is pulled:

```bash
ollama pull llama3.1:8b
```

Gemini demo mode uses hosted Gemini embeddings and chat:

```bash
EMBEDDING_PROVIDER=gemini
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_key_here
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_LLM_MODEL=gemini-2.5-flash
```

OpenAI is still supported by setting `EMBEDDING_PROVIDER=openai` and/or `LLM_PROVIDER=openai` with `OPENAI_API_KEY`.

When switching embedding providers, delete `backend/storage/chroma` and re-analyze videos. Chroma collections should not mix vectors created by different embedding models.

## Phase 2: YouTube analysis

YouTube metadata is fetched with `yt-dlp` without downloading the video. Captions are fetched with `youtube-transcript-api` when they are available.

Engagement rate is calculated as:

```text
(likes + comments) / views * 100
```

The result is rounded to 2 decimal places. If the view count is missing or zero, engagement rate is returned as `null`.

External platforms sometimes return inconsistent metadata types, so duration is normalized into whole seconds before the API returns it.

Start the backend and test the endpoint:

```bash
curl -X POST http://127.0.0.1:8000/api/videos/youtube/analyze \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

The same endpoint is also available in Swagger at `http://127.0.0.1:8000/docs`.

## Phase 3: Instagram Reel analysis

Instagram metadata is fetched with `yt-dlp`. Some public Reels work without extra setup, but Instagram often blocks scraping or asks for login, so this endpoint returns a clean `400` if metadata cannot be fetched.

If audio can be downloaded, Whisper is used as a transcript fallback. If audio download or transcription fails, the API still returns the metadata it found with an empty transcript and `transcript_source` set to `"unavailable"`.

To use cookies, set this in `backend/.env`:

```bash
INSTAGRAM_COOKIES_FILE=/path/to/instagram-cookies.txt
```

Test the endpoint with a public Reel URL:

```bash
curl -X POST http://127.0.0.1:8000/api/videos/instagram/analyze \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.instagram.com/reel/SHORTCODE/"}'
```

## Phase 4: RAG ingestion

When an analysis endpoint returns transcript text, the backend splits it into overlapping chunks and stores those chunks in ChromaDB under the `social_videos` collection. Chroma was picked for local development because it persists to disk and does not require another service while the retrieval flow is still being built.

Chunking uses LangChain's `RecursiveCharacterTextSplitter` with `chunk_size=700` and `chunk_overlap=120`. That keeps chunks large enough to preserve context, while the overlap helps avoid losing meaning at chunk boundaries.

Embeddings use OpenAI's `text-embedding-3-small` model. It is a practical default for this phase because it is inexpensive, fast enough for short transcripts, and easy to swap later if the storage layer changes.

Set `OPENAI_API_KEY` in `backend/.env` before testing ingestion:

```bash
OPENAI_API_KEY=your_key_here
```

Analysis responses include ingestion status separately from extraction:

```json
"rag_ingestion": {
  "status": "success",
  "stored_chunks": 8,
  "collection_name": "social_videos",
  "error": null
}
```

If embeddings are not configured or Chroma fails, the endpoint can still return the extracted metadata and transcript with `"status": "failed"`. If no transcript is available, ingestion returns `"status": "skipped"`.

Local vectors are stored under `backend/storage/chroma`.

## Graceful degradation strategy

Metadata and transcript extraction run independently from vector ingestion. That means a YouTube or Instagram analysis can still return useful data even when optional AI infrastructure is missing.

Embeddings are treated as infrastructure, not as a requirement for extraction. If `OPENAI_API_KEY` is missing or the vector store cannot write, the API includes a `rag_ingestion` failure object instead of failing the whole request.

This keeps the current API useful during local setup, provider outages, and partial deployments. The chat layer can later decide whether to rely on stored chunks or ask the user to retry ingestion.

## Phase 5: Chat with citations

The chat endpoint retrieves relevant transcript chunks from Chroma and answers from those chunks with citations. Analyze at least one video first so transcript chunks exist in `backend/storage/chroma`.

Configure the selected embedding and chat providers before using retrieval chat. Local mode uses HuggingFace embeddings and Ollama; Gemini mode needs `GOOGLE_API_KEY`.

Chat supports video-specific questions through metadata-aware retrieval. In workspace sessions, `Video A` and `Video B` map to the stored workspace videos, so prompts like `Summarize Video A` or `What is the main topic of Video B?` retrieve chunks from the right video instead of searching for those UI labels inside transcript text.

Chat prompts include both transcript chunks and workspace metadata. Transcripts answer what was said, while metadata handles identity and metrics such as creator, title, platform, views, likes, comments, engagement rate, and transcript availability.

```bash
curl -X POST http://127.0.0.1:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo-session",
    "message": "What is the main point of the video?"
  }'
```

Response shape:

```json
{
  "session_id": "demo-session",
  "answer": "...",
  "citations": [
    {
      "video_id": "...",
      "platform": "youtube",
      "creator": "...",
      "chunk_index": 0,
      "source_url": "..."
    }
  ]
}
```

If no chunks are available yet, the endpoint returns a helpful message instead of crashing.

For streamed answer text, use:

```bash
curl -N -X POST http://127.0.0.1:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo-session",
    "message": "What is the main point of the video?"
  }'
```

The frontend will consume this later with `fetch` streaming. The streaming endpoint sends plain answer text only; citation objects stay on the non-streaming endpoint for now.

## Comparison workspace

The workspace endpoint analyzes two videos and stores them as Video A and Video B for comparison flows. It supports YouTube and Instagram combinations, including YouTube vs YouTube, YouTube vs Instagram, and Instagram vs Instagram.

```bash
curl -X POST http://127.0.0.1:8000/api/workspace/create \
  -H "Content-Type: application/json" \
  -d '{
    "video_a_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "video_b_url": "https://www.instagram.com/reel/SHORTCODE/"
  }'
```

Response shape:

```json
{
  "workspace_id": "...",
  "video_a": {},
  "video_b": {}
}
```

Fetch a stored workspace:

```bash
curl http://127.0.0.1:8000/api/workspace/WORKSPACE_ID
```

Compare the stored videos:

```bash
curl http://127.0.0.1:8000/api/workspace/WORKSPACE_ID/compare
```

The comparison response includes a winner, both scores, strengths for each video, and improvement suggestions. It uses available metadata only, so missing Instagram metrics do not break the report.

Workspaces are in-memory for now, so they reset when the backend restarts.

## Notes

Instagram extraction needs to be handled carefully. Reels can behave differently depending on availability, region, cookies, and auth, so this code treats extraction as best effort instead of assuming one path will always work.

The current chat work uses in-memory session history. Persistent chat memory still needs to be added.
