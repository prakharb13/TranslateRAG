# TranslateRAG

A RAG-enhanced translation app using Google's TranslateGemma 4B model via Ollama. Upload domain-specific documents to improve translation quality for specialized terminology.

## Architecture

```
User -> Streamlit UI -> FastAPI Backend -> Ollama (TranslateGemma 4B)
                              |
                         ChromaDB (RAG)
```

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running

## Setup

### 1. Install Ollama and pull the model

```bash
# Install Ollama from https://ollama.com/download
# Then pull TranslateGemma:
ollama pull translategemma:4b
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

## Running

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
RAGTRANSLATE/
├── backend/
│   ├── main.py               # FastAPI app with CORS
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
│   └── app.py                 # Streamlit UI
├── data/chroma_db/            # Vector database storage
├── uploads/                   # Uploaded document files
├── requirements.txt
└── .env.example
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
