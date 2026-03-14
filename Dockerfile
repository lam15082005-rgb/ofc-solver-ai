# syntax=docker/dockerfile:1

FROM python:3.13-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps + build tools for C++ framework
# Install Boost, python3-pip for gdown (handles large Google Drive files)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    g++ \
    make \
    libboost-all-dev \
    python3-dev \
    git \
    python3-pip \
  && pip3 install --no-cache-dir gdown \
  && rm -rf /var/lib/apt/lists/*

# Install python deps first (better layer caching)
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy framework source and build
COPY framework /app/framework
WORKDIR /app/framework
RUN chmod +x build_linux.sh && ./build_linux.sh

# Copy app source
WORKDIR /app
COPY backend /app/backend
COPY frontend /app/frontend
COPY users.json /app/users.json

# Create runtime-writable dirs (Railway filesystem is writable but ephemeral)
RUN mkdir -p /app/sessions /app/backend/lookup

# Download pre-generated lookup table from Google Drive
RUN echo "📥 Downloading lookup table from Google Drive..." && \
    gdown --id 1CQ7VN5WaJheWs9MGcTmOPEZQtqkzxYvv \
      -O /app/backend/lookup/13-ranks-4-duplicate-suits-with-jokers.dat && \
    echo "✅ Lookup table downloaded ($(du -h /app/backend/lookup/13-ranks-4-duplicate-suits-with-jokers.dat | cut -f1))" && \
    ls -lh /app/backend/lookup/

# Make lookup directory writable (Railway has writable filesystem)
RUN chmod 777 /app/backend/lookup

EXPOSE 8080

# Ensure lookup is accessible from backend working directory
RUN ln -sf /app/backend/lookup /app/lookup || true

# Railway sets $PORT; default to 8080 for local runs
# Run from /app/backend so solver finds "lookup" directory
CMD ["sh", "-c", "cd /app/backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
