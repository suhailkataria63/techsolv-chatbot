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