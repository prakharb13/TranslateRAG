import uuid
from typing import Optional, List, Dict

import chromadb
from sentence_transformers import SentenceTransformer

from backend.config import CHROMA_DB_PATH, EMBEDDING_MODEL

_embedding_model: Optional[SentenceTransformer] = None
_chroma_client: Optional[chromadb.PersistentClient] = None

COLLECTION_NAME = "documents"


def _get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model


def _get_collection() -> chromadb.Collection:
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return _chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _embed(texts: List[str]) -> List[List[float]]:
    model = _get_embedding_model()
    return model.encode(texts, show_progress_bar=False).tolist()


def add_documents(chunks: List[str], filename: str) -> str:
    """Store chunks in ChromaDB. Returns a document group id."""
    collection = _get_collection()
    doc_id = uuid.uuid4().hex[:12]
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    embeddings = _embed(chunks)
    metadatas = [{"filename": filename, "doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))]
    collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
    return doc_id


def query_similar(text: str, n_results: int = 3) -> List[str]:
    collection = _get_collection()
    if collection.count() == 0:
        return []
    embeddings = _embed([text])
    results = collection.query(query_embeddings=embeddings, n_results=min(n_results, collection.count()))
    return results["documents"][0] if results["documents"] else []


def list_documents() -> List[Dict]:
    collection = _get_collection()
    if collection.count() == 0:
        return []
    all_data = collection.get(include=["metadatas"])
    docs: Dict[str, Dict] = {}
    for meta in all_data["metadatas"]:
        did = meta["doc_id"]
        if did not in docs:
            docs[did] = {"id": did, "filename": meta["filename"], "chunk_count": 0}
        docs[did]["chunk_count"] += 1
    return list(docs.values())


def delete_document(doc_id: str) -> bool:
    collection = _get_collection()
    all_data = collection.get(include=["metadatas"])
    ids_to_delete = [
        id_ for id_, meta in zip(all_data["ids"], all_data["metadatas"])
        if meta.get("doc_id") == doc_id
    ]
    if not ids_to_delete:
        return False
    collection.delete(ids=ids_to_delete)
    return True
