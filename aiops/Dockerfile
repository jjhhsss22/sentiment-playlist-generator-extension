FROM python:3.11-slim

WORKDIR /app

# Install minimal system deps (needed for MySQL + general stability)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Run the analyzer loop
CMD ["python", "run_analyzer.py"]