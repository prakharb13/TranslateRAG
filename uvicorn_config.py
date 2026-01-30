# Uvicorn configuration
# Usage: uvicorn backend.main:app --reload --reload-dir backend --reload-dir frontend

# This config watches only the backend and frontend directories,
# excluding venv, data, uploads, and other non-code directories

reload_excludes = [
    "venv/*",
    "*.pyc",
    "__pycache__/*",
    "data/*",
    "uploads/*",
    ".git/*",
    "*.db",
]

reload_includes = [
    "*.py",
]
