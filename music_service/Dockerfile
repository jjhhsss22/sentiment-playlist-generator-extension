FROM python:3.11-slim

WORKDIR /app

# Minimal system deps (only if requests / SSL needed)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Default command (overridden by docker-compose)
CMD ["celery", "-A", "celery_worker.celery", "worker", "--loglevel=info"]