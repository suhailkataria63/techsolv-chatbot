# Social Video RAG Chatbot

A full-stack app for asking questions about short social videos.

The finished version will accept one YouTube URL and one Instagram Reel URL, pull transcript and metadata where available, calculate engagement rate, store transcript chunks in a vector database, and provide a streaming LangChain-based chat interface with citations and conversation memory.

## Current status

Phase 3 backend extraction. The repo has a small FastAPI backend with health checks, YouTube analysis, and an Instagram Reel analysis endpoint. RAG storage, chat, and the frontend are still intentionally left out.

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

## Notes

Instagram extraction needs to be handled carefully. Reels can behave differently depending on availability, region, cookies, and auth, so this code treats extraction as best effort instead of assuming one path will always work.

No RAG pipeline, frontend UI, or database logic is implemented yet.
