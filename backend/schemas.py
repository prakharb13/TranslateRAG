from typing import List
from pydantic import BaseModel


class TranslateRequest(BaseModel):
    text: str
    source_language: str
    target_language: str
    use_rag: bool = True


class TranslateResponse(BaseModel):
    translated_text: str
    rag_context_used: bool
    context_snippets: List[str] = []


class DocumentTranslateResponse(BaseModel):
    translated_chunks: List[str]
    full_translation: str
    source_language: str
    target_language: str


class AskRequest(BaseModel):
    question: str
    source_language: str
    target_language: str


class AskResponse(BaseModel):
    answer: str
    context_snippets: List[str]
    mode: str = "rag"


class DocumentInfo(BaseModel):
    id: str
    filename: str
    chunk_count: int
