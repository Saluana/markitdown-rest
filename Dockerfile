FROM alpine:3.19

# Set environment variables and locale
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONIOENCODING=UTF-8

# Install system dependencies and Python
RUN apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev \
    ffmpeg \
    exiftool \
    build-base \
    pango-dev \
    cairo-dev \
    jpeg-dev \
    zlib-dev \
    gcc \
    musl-dev \
    libffi-dev \
    git

WORKDIR /app

# Create and activate virtual environment
RUN python3 -m venv .venv

# Install dependencies with extras
COPY requirements.txt .
RUN . .venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt --upgrade

# Copy application code
COPY . .

# Expose the port
EXPOSE 8000

# Run using the full path to uvicorn
CMD [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
