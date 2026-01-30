# Use Python 3.11 slim image (Debian-based, smaller than full)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for layer caching)
# If requirements don't change, Docker reuses this layer
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir: Don't cache pip downloads (saves ~100MB)
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ /app/backend/

# Create uploads and data directories
RUN mkdir -p /app/uploads /app/data

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8000 (documentation, doesn't publish)
EXPOSE 8000

# Start uvicorn server
# --host 0.0.0.0: Listen on all interfaces (required in Docker)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
