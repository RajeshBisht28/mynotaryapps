FROM python:3.11-slim

WORKDIR /app

# System dependencies (grouped, minimal but sufficient)
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libcairo2-dev \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    libgeos-dev \
    libharfbuzz-dev \
    poppler-utils \
    tesseract-ocr \
    libssl-dev \
    p11-kit \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
