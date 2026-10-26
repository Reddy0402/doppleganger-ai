FROM python:3.11-slim

# Install system dependencies for OpenCV and OpenBLAS
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Prevent OpenBLAS thread allocation issues on small container memory
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend \
    OPENBLAS_NUM_THREADS=1 \
    PORT=8000

# Install Python requirements
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy application and data
COPY backend/ ./backend/
COPY data/ ./data/

# Download the ONNX models at build time if not present
RUN python backend/scripts/download_models.py

EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
