# Social Video RAG Chatbot

A full-stack app for asking questions about short social videos.

The finished version will accept one YouTube URL and one Instagram Reel URL, pull transcript and metadata where available, calculate engagement rate, store transcript chunks in a vector database, and provide a streaming LangChain-based chat interface with citations and conversation memory.

## Current status

Phase 1 scaffold. The repo has a small FastAPI backend with a health endpoint and the project notes needed before building extraction, storage, and chat features.

## Planned stack

- FastAPI for the backend API
- Next.js for the frontend
- LangChain for the RAG chat flow
- Chroma for local vector storage
- OpenAI for embeddings and chat responses
- YouTube and Instagram metadata/transcript extraction, added in a later phase

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

## Notes

Instagram extraction will need to be handled carefully later. Reels can behave differently depending on availability, region, cookies, and auth, so that part should have a fallback path instead of assuming one extractor will always work.

No video extraction, RAG pipeline, frontend UI, or database logic is implemented yet.
