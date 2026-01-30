from typing import List
from pathlib import Path
import shutil

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.schemas import TranslateRequest, TranslateResponse, DocumentTranslateResponse, AskRequest, AskResponse
from backend.services import model_service, rag_service, document_service
from backend.config import UPLOAD_DIR

router = APIRouter(prefix="/api")


@router.post("/translate", response_model=TranslateResponse)
async def translate(req: TranslateRequest):
    context_snippets: List[str] = []

    if req.use_rag:
        context_snippets = rag_service.query_similar(req.text)

    context = "\n---\n".join(context_snippets) if context_snippets else None

    translated = model_service.translate(
        text=req.text,
        source_language=req.source_language,
        target_language=req.target_language,
        context=context,
    )

    return TranslateResponse(
        translated_text=translated,
        rag_context_used=bool(context_snippets),
        context_snippets=context_snippets,
    )


@router.post("/translate-document", response_model=DocumentTranslateResponse)
async def translate_document(
    file: UploadFile = File(...),
    source_language: str = Form(...),
    target_language: str = Form(...),
):
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
    if not text.strip():
        raise HTTPException(400, "No text could be extracted from the document.")

    chunks = document_service.chunk_text(text, chunk_size=1000, overlap=0)

    translated_chunks: List[str] = []
    for chunk in chunks:
        translated = model_service.translate(
            text=chunk,
            source_language=source_language,
            target_language=target_language,
        )
        translated_chunks.append(translated)

    return DocumentTranslateResponse(
        translated_chunks=translated_chunks,
        full_translation="\n\n".join(translated_chunks),
        source_language=source_language,
        target_language=target_language,
    )


@router.post("/ask", response_model=AskResponse)
async def ask_question(req: AskRequest):
    if req.use_rag:
        context_snippets = rag_service.query_similar(req.question, n_results=5)
        context = "\n---\n".join(context_snippets) if context_snippets else ""

        answer = model_service.answer_question(
            question=req.question,
            context=context,
            source_language=req.source_language,
            target_language=req.target_language,
        )
        return AskResponse(answer=answer, context_snippets=context_snippets, mode="rag")

    translated = model_service.translate(
        text=req.question,
        source_language=req.source_language,
        target_language=req.target_language,
    )
    return AskResponse(answer=translated, context_snippets=[], mode="translation")
