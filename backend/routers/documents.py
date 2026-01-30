import shutil
from typing import List
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.config import UPLOAD_DIR
from backend.schemas import DocumentInfo
from backend.services import document_service, rag_service

router = APIRouter(prefix="/api/documents")


@router.post("/upload", response_model=DocumentInfo)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "No filename provided")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".pdf", ".txt", ".docx"):
        raise HTTPException(400, f"Unsupported file type: {suffix}. Use PDF, TXT, or DOCX.")

    upload_path = Path(UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    dest = upload_path / file.filename

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    text = document_service.extract_text(str(dest))
    chunks = document_service.chunk_text(text)

    if not chunks:
        raise HTTPException(400, "No text could be extracted from the document.")

    doc_id = rag_service.add_documents(chunks, file.filename)

    return DocumentInfo(id=doc_id, filename=file.filename, chunk_count=len(chunks))


@router.get("", response_model=List[DocumentInfo])
async def list_documents():
    docs = rag_service.list_documents()
    return [DocumentInfo(**d) for d in docs]


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    deleted = rag_service.delete_document(doc_id)
    if not deleted:
        raise HTTPException(404, "Document not found")
    return {"status": "deleted"}
