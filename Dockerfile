FROM python:3.11-slim

WORKDIR /app

# Install system dependencies, OpenCV libraries, Tesseract OCR, and development headers
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install English and Bangla traineddata
RUN apt-get update && apt-get install -y \
    tesseract-ocr-eng \
    tesseract-ocr-ben \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

RUN tesseract --version

# Run FastAPI with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]