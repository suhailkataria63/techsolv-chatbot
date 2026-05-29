# Social Video RAG Chatbot

A full-stack app for asking questions about short social videos.

The finished version will accept one YouTube URL and one Instagram Reel URL, pull transcript and metadata where available, calculate engagement rate, store transcript chunks in a vector database, and provide a streaming LangChain-based chat interface with citations and conversation memory.

## Current status

Phase 2 backend extraction. The repo has a small FastAPI backend with health checks and a YouTube analysis endpoint. RAG storage, chat, Instagram support, and the frontend are still intentionally left out.

## Planned stack

- FastAPI for the backend API
- Next.js for the frontend
- LangChain for the RAG chat flow
- Chroma for local vector storage
- OpenAI for embeddings and chat responses
- yt-dlp for YouTube metadata
- youtube-transcript-api for YouTube transcripts
- Instagram metadata/transcript extraction, added in a later phase

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

## Phase 2: YouTube analysis

YouTube metadata is fetched with `yt-dlp` without downloading the video. Captions are fetched with `youtube-transcript-api` when they are available.

Engagement rate is calculated as:

```text
(likes + comments) / views * 100
```

The result is rounded to 2 decimal places. If the view count is missing or zero, engagement rate is returned as `null`.

Start the backend and test the endpoint:

```bash
curl -X POST http://127.0.0.1:8000/api/videos/youtube/analyze \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

The same endpoint is also available in Swagger at `http://127.0.0.1:8000/docs`.

## Notes

Instagram extraction will need to be handled carefully later. Reels can behave differently depending on availability, region, cookies, and auth, so that part should have a fallback path instead of assuming one extractor will always work.

No RAG pipeline, frontend UI, Instagram extraction, or database logic is implemented yet.
