# TranslateRAG

A RAG-enhanced translation app using Google's TranslateGemma 4B model via Ollama. Upload domain-specific documents to improve translation quality for specialized terminology.

## Architecture

```
User -> Streamlit UI -> FastAPI Backend -> Ollama (TranslateGemma 4B)
                              |
                         ChromaDB (RAG)
```

## Prerequisites

### For Docker Deployment (Recommended)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- docker-compose (included with Docker Desktop)

### For Local Development
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running

## Deployment Options

Choose one of the following deployment methods:

### Option A: Docker Deployment (Recommended)

This runs everything in containers - simpler and consistent across environments.

**1. Clone the repository**

```bash
git clone <repo-url>
cd TranslateRAG
```

**2. Start all services with Docker Compose**

```bash
# Build and start all containers
docker-compose up -d

# Wait for Ollama to be healthy (check status)
docker-compose ps

# Pull the TranslateGemma model (~4GB, first time only)
docker-compose exec ollama ollama pull translategemma:latest
```

**3. Access the application**

- Frontend UI: http://localhost:8501
- Backend API: http://localhost:8000/docs
- Ollama: http://localhost:11434

**Useful Docker commands:**

```bash
# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Check service status
docker-compose ps
```

---

### Option B: Local Development Setup

### 1. Install Ollama and pull the model

```bash
# Install Ollama from https://ollama.com/download
# Then pull TranslateGemma:
ollama pull translategemma:latest
```

### 2. Clone and set up the project

```bash
git clone <repo-url>
cd RAGTranslate

# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure environment (optional)

```bash
cp .env.example .env
# Edit .env if you need to change defaults (Ollama URL, model name, etc.)
```

**Running locally (Option B only)**

You need three terminals (activate the venv in each):

**Terminal 1 — Ollama:**
```bash
ollama serve
```

**Terminal 2 — Backend (FastAPI):**
```bash
cd RAGTranslate
source venv/bin/activate   # or venv\Scripts\activate on Windows
uvicorn backend.main:app --reload
```
API will be at http://localhost:8000 (docs at http://localhost:8000/docs)

**Terminal 3 — Frontend (Streamlit):**
```bash
cd RAGTranslate
source venv/bin/activate   # or venv\Scripts\activate on Windows
streamlit run frontend/app.py
```
UI will open at http://localhost:8501

## Usage

### Translate Document
1. Open the Streamlit UI
2. Go to the **Translate Document** tab
3. Select source and target languages
4. Upload a PDF, TXT, or DOCX file
5. Click **Translate Document** — the entire file will be translated chunk by chunk
6. Download the result as a TXT file

### Ask Questions (RAG)
1. Go to the **Manage Documents** tab and upload/index one or more documents
2. Go to the **Ask Questions (RAG)** tab
3. Select the document language and the language you want the answer in
4. Type your question and click **Ask**
5. The system retrieves relevant passages from indexed documents, then generates and translates the answer

## Project Structure

```
TranslateRAG/
├── backend/
│   ├── Dockerfile             # Backend container definition
│   ├── main.py                # FastAPI app with CORS
│   ├── config.py              # Settings from environment variables
│   ├── schemas.py             # Pydantic request/response models
│   ├── routers/
│   │   ├── translate.py       # POST /api/translate
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
├── .env.example              # Environment variables template
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/translate` | Translate text with optional RAG context |
| POST | `/api/translate-document` | Translate an entire uploaded document |
| POST | `/api/ask` | Ask a question answered using RAG context |
| POST | `/api/documents/upload` | Upload and index a document |
| GET | `/api/documents` | List indexed documents |
| DELETE | `/api/documents/{id}` | Remove a document from the index |
| GET | `/api/languages` | List supported languages |

---

## Docker Architecture

When running with Docker, the application consists of three containers:

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

**Docker Networking:**
- Containers communicate via Docker's internal network using service names
- Frontend connects to backend at `http://backend:8000`
- Backend connects to Ollama at `http://ollama:11434`

**Data Persistence:**
- `./data` → ChromaDB vector database
- `./uploads` → Uploaded documents
- `ollama-models` → Downloaded Ollama models (Docker volume)

**Security:**
- Containers run as non-root user (UID 1000)
- No secrets baked into images (configured via environment variables)

---

## Deployment Notes

### Local Development
- Use Docker for consistent environment
- Data persists in local folders (`./data`, `./uploads`)
- Model downloaded once and cached

### Production (EC2)
- Same Docker setup works on EC2
- Use security groups to control access
- Consider using reverse proxy (Nginx) for HTTPS
- Set up proper backup for `./data` and `./uploads`

### Environment Variables

Configure via `docker-compose.yml` or `.env` file:

- `OLLAMA_BASE_URL` - Ollama API endpoint
- `MODEL_NAME` - Ollama model name
- `CHROMA_DB_PATH` - ChromaDB storage path
- `UPLOAD_DIR` - Document upload directory
- `EMBEDDING_MODEL` - Sentence transformer model
- `BACKEND_URL` - Backend API URL (frontend only)
