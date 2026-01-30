import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "translategemma:4b")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", str(BASE_DIR / "data" / "chroma_db"))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

SUPPORTED_LANGUAGES = [
    "Arabic", "Chinese (Simplified)", "Czech", "Dutch", "English",
    "French", "German", "Hindi", "Italian", "Japanese", "Korean",
    "Polish", "Portuguese", "Russian", "Spanish", "Swedish",
    "Thai", "Turkish", "Ukrainian", "Vietnamese",
]
