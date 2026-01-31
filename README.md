# TranslateRAG

A multilingual translation and Q&A app powered by Google's TranslateGemma 4B model via Ollama, supporting 20 languages. Uses RAG with ChromaDB to improve translation quality using domain-specific documents. Fully containerized with Docker Compose (Streamlit + FastAPI + Ollama) for deployment on local machines or AWS EC2.

## Live Demo

The app is deployed on AWS EC2 and accessible at:

- **Frontend UI:** http://34.200.170.162:8501
- **Backend API:** http://34.200.170.162:8000/docs

> The EC2 server may not always be running. Contact the owner to request access.

## Architecture

```
User -> Streamlit UI -> FastAPI Backend -> Ollama (TranslateGemma 4B)
                              |
                         ChromaDB (RAG)
```

```
┌─────────────────┐
│   Frontend      │ :8501 (Streamlit)
│  (Container)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Backend      │ :8000 (FastAPI)
│  (Container)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Ollama      │ :11434 (TranslateGemma)
│  (Container)    │
└─────────────────┘
```

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- docker-compose (included with Docker Desktop)

## How to Use

### Option 1: Use the Live EC2 Deployment

The app is already deployed on AWS EC2 (Ubuntu, t3.large) and ready to use. Simply open the links above in your browser. Contact the owner if the server is not running.

> Note: Data uploaded to the EC2 server is shared and not private.

### Option 2: Run Locally with Docker

If you want full control over your data and privacy, run everything locally:

```bash
git clone <repo-url>
cd TranslateRAG
docker compose up -d --build
docker exec translaterag-ollama ollama pull translategemma:latest
```

Access the app at http://localhost:8501

All data stays on your machine in `./data` and `./uploads`.

**Useful Docker commands:**

```bash
docker compose logs -f           # View all logs
docker compose logs -f backend   # View backend logs
docker compose down              # Stop all services
docker compose up -d --build     # Rebuild after code changes
docker compose ps                # Check service status
```

## Usage

### Translate Document
1. Open the **Translate Document** tab
2. Select source and target languages
3. Upload a PDF, TXT, or DOCX file
4. Click **Translate Document** — the file is translated chunk by chunk
5. Download the result as a TXT file

### Ask Questions (RAG)
1. Go to **Manage Documents** and upload/index documents
2. Go to the **Ask Questions** tab
3. Select languages, type your question, and click **Submit**
4. The system retrieves relevant passages from indexed documents and generates an answer in the target language

## Project Structure

```
TranslateRAG/
├── backend/
│   ├── Dockerfile             # Backend container definition
│   ├── main.py                # FastAPI app with CORS
│   ├── config.py              # Settings from environment variables
│   ├── schemas.py             # Pydantic request/response models
│   ├── routers/
│   │   ├── translate.py       # Translation and Q&A endpoints
│   │   └── documents.py       # Upload, list, delete documents
│   └── services/
│       ├── model_service.py   # Ollama client for TranslateGemma
│       ├── rag_service.py     # ChromaDB + sentence-transformers
│       └── document_service.py# PDF/TXT/DOCX parsing and chunking
├── frontend/
│   ├── Dockerfile             # Frontend container definition
│   └── app.py                 # Streamlit UI
├── data/chroma_db/            # Vector database storage (persisted)
├── uploads/                   # Uploaded document files (persisted)
├── docker-compose.yml         # Multi-container orchestration
├── requirements.txt           # Python dependencies
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/translate` | Translate text with optional RAG context |
| POST | `/api/translate-document` | Translate an entire uploaded document |
| POST | `/api/ask` | Ask a question or translate with RAG context |
| POST | `/api/documents/upload` | Upload and index a document |
| GET | `/api/documents` | List indexed documents |
| DELETE | `/api/documents/{id}` | Remove a document from the index |
| GET | `/api/languages` | List supported languages |

## Environment Variables

Configure via `docker-compose.yml` or `.env` file:

| Variable | Description |
|----------|-------------|
| `OLLAMA_BASE_URL` | Ollama API endpoint |
| `MODEL_NAME` | Ollama model name |
| `CHROMA_DB_PATH` | ChromaDB storage path |
| `UPLOAD_DIR` | Document upload directory |
| `EMBEDDING_MODEL` | Sentence transformer model |
| `BACKEND_URL` | Backend API URL (frontend only) |
