FROM python:3.11-slim

WORKDIR /app

# System dependencies (needed for MySQL + building wheels)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Default command (overridden by docker-compose for workers)
CMD ["python", "run_db.py"]