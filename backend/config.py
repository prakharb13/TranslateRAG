import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH")
UPLOAD_DIR = os.getenv("UPLOAD_DIR")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

SUPPORTED_LANGUAGES = [
    "Arabic", "Chinese (Simplified)", "Czech", "Dutch", "English",
    "French", "German", "Hindi", "Italian", "Japanese", "Korean",
    "Polish", "Portuguese", "Russian", "Spanish", "Swedish",
    "Thai", "Turkish", "Ukrainian", "Vietnamese",
]
