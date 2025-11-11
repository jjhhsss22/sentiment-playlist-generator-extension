FROM python:3.11-slim


WORKDIR /app


RUN apt-get update && apt-get install -y \
    ca-certificates \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ca-certificates = for HTTPS requests
# git = just incase repository cloning needed
# curl = for health checks or debugging


COPY ai_requirements.txt .
RUN pip install --no-cache-dir -r ai_requirements.txt


RUN python -m nltk.downloader punkt punkt_tab -d /usr/local/share/nltk_data
ENV NLTK_DATA=/usr/local/share/nltk_data

# need to download external data separately for NLTK


COPY . .


EXPOSE 8001


CMD ["python", "api_ai_service_interface.py"]