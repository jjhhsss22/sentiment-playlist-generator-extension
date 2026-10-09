FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ca-certificates \
    git \
    curl \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# NLTK data
RUN python -m nltk.downloader punkt punkt_tab -d /usr/local/share/nltk_data
ENV NLTK_DATA=/usr/local/share/nltk_data

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# default (can be overridden by docker-compose)
CMD ["celery", "-A", "celery_worker.celery", "worker", "--loglevel=info", "--pool=solo"]