FROM python:3.10-slim

WORKDIR /app

# System dependencies (minimal but sufficient)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ben \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (cache friendly)
COPY requirements.txt .

# Install dependencies with CPU-only torch
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# Copy app source (will be overridden by volume in dev)
COPY . .

# Expose port
EXPOSE 8000

# Default command (overridden by docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]