# Production Dockerfile
FROM python:3.12-slim

WORKDIR /workspace

# Install system dependencies (including Tesseract OCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy backend dependencies
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt greenlet

# Copy source code
COPY app/ app/
COPY sme_platform.db .

# Expose port
EXPOSE 8000

# Run Uvicorn server
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
