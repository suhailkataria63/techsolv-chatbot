# Social Video RAG Chatbot

A Retrieval-Augmented Generation (RAG) app that analyzes YouTube and Instagram videos, compares engagement metrics, ingests transcripts into a vector database, and answers grounded questions using transcript retrieval plus metadata-aware search.

Built as a submission for the Full Stack AI Engineer Technical Round.

---

## Features

### Video Analysis

* Analyze YouTube videos
* Analyze Instagram Reels
* Extract video metadata
* Retrieve or generate transcripts
* Calculate engagement metrics
* Compare content performance

### RAG Pipeline

* Transcript chunking
* Embedding generation
* ChromaDB vector storage
* Metadata-aware retrieval
* Position-aware retrieval
* Citation-backed responses

### Chat Capabilities

* Grounded transcript Q&A
* Video A / Video B referencing
* Beginning / middle / end transcript retrieval
* Multi-video comparison
* Session-aware conversations
* Streaming responses

### LLM Support

* Gemini API
* Ollama (local execution)

---

## Architecture

Frontend

* Next.js
* React
* TypeScript

Backend

* FastAPI
* LangChain

Retrieval Layer

* ChromaDB
* HuggingFace Embeddings
* Metadata-aware retrieval
* Position-aware retrieval

Models

* Gemini
* Ollama

Transcript Sources

* YouTube Transcript API
* Whisper

---

## Retrieval Workflow

1. User submits video URLs
2. Metadata is extracted
3. Transcripts are collected
4. Transcript text is chunked
5. Embeddings are generated
6. Chunks are stored in ChromaDB
7. User asks a question
8. Relevant transcript chunks are retrieved
9. Retrieved context is sent to the LLM
10. Grounded answer is generated with citations

---

## Grounding Strategy

The chatbot is designed to minimize hallucinations.

Rules:

* Transcript content is the source of spoken information.
* Metadata is the source of creator, platform, title, engagement, and video information.
* Responses are generated only from retrieved transcript chunks and stored metadata.
* Unsupported questions return an insufficient-context response.
* Position-aware retrieval is used for beginning, middle, and end transcript questions.

---

## Example Questions

### Video Understanding

* Summarize Video A
* What is the main topic of Video A?
* What happens at the beginning of Video A?
* What happens near the end of Video A?
* What happens in the middle of Video A?

### Comparison

* Compare Video A and Video B
* Compare the hooks in the first 5 seconds
* Which video has stronger engagement?
* Which video contains more transcript content?

### Content Retrieval

* What did the speaker say about AI?
* What advice was given in Video A?
* What topic is discussed most frequently?

---

## Running Locally

### Backend

```bash
cd backend

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
````

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

## Environment Variables

Backend

```env
GOOGLE_API_KEY=your_gemini_api_key

LLM_PROVIDER=gemini
```

For Ollama:

```env
LLM_PROVIDER=ollama

OLLAMA_MODEL=llama3.2:3b
```

---

## Deployment

### Backend on Render

The backend can be deployed as a Render web service from `backend/`.

Render settings:

```text
Build command: pip install -r requirements.txt
Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

There is also a starter blueprint at `backend/render.yaml`. Render provides `PORT` automatically, while local development can keep using:

```bash
uvicorn app.main:app --reload
```

Set backend environment variables in Render:

```env
ENV=production
EMBEDDING_PROVIDER=gemini
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_LLM_MODEL=gemini-2.5-flash
CHROMA_DIR=./storage/chroma
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,https://your-vercel-app.vercel.app
```

`INSTAGRAM_COOKIES_FILE` is optional and only needed if you add cookie-based Instagram extraction later. Do not commit API keys or cookie files.

Render free instances may restart or lose local disk state. Since Chroma is currently stored under `backend/storage/chroma`, vectors may need to be rebuilt by re-analyzing videos after a reset. For production, use persistent disk or move vectors to Qdrant, Pinecone, or Postgres with pgvector.

### Frontend on Vercel

Deploy the `frontend/` folder as the Vercel project root.

Vercel settings:

```text
Build command: npm run build
Output: Next.js default
```

Set this frontend environment variable in Vercel:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-render-api.onrender.com
```

For local development, `frontend/.env.example` uses:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

After deploying the frontend, add the Vercel URL to backend `CORS_ORIGINS` on Render.

---

## Project Structure

```text
backend/
├── app/
│   ├── chat/
│   ├── comparison/
│   ├── rag/
│   ├── workspace/
│   └── main.py

frontend/
├── src/
├── components/
├── pages/

storage/
└── chroma/
```

---

## Key Technical Highlights

* Retrieval-Augmented Generation (RAG)
* Metadata-aware retrieval
* Position-aware transcript retrieval
* ChromaDB vector search
* Multi-video analysis workflow
* Provider switching between Gemini and Ollama
* Citation-backed grounded responses
* FastAPI backend architecture
* React / Next.js frontend

---

## Future Improvements

* Multi-video workspace history
* Hybrid keyword + vector retrieval
* Advanced transcript summarization
* Video chapter generation
* Analytics dashboard
* Cloud deployment

---

## Author

Suhail Kataria

Full Stack AI Engineer Internship Submission
Techsolv IT Services
