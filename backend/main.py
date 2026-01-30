from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import SUPPORTED_LANGUAGES
from backend.routers import translate, documents

app = FastAPI(title="TranslateRAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(translate.router)
app.include_router(documents.router)


@app.get("/api/languages")
async def get_languages():
    return {"languages": SUPPORTED_LANGUAGES}
