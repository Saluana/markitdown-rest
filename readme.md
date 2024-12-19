# File to Markdown API

A FastAPI-based service built on top of Microsoft's MarkItDown library that provides endpoints for converting various document formats to markdown and extracting YouTube video transcripts.
This project extends MarkItDown's capabilities with additional features specifically focused on YouTube transcript extraction and web content conversion.

## Features

-   Convert various file formats to markdown
-   Extract YouTube video transcripts with timestamps
-   URL content conversion
-   Support for multiple document formats including:
    -   HTML
    -   PDF
    -   DOCX
    -   XLSX
    -   PPTX
    -   Images
    -   Audio files (WAV, MP3)
    -   ZIP files
    -   Wikipedia pages
    -   YouTube pages / Videos

## Installation

1. Clone the repository
2. Create a `.env` file with the following variables:

```env
PROXY_URL=your_proxy_url_if_needed
OPENAI_API_KEY=your_openai_api_key
```

3. Build and run using Docker:

```bash
docker build -t document-converter .
docker run -p 8000:8000 document-converter
```

Or install locally:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### 1. Convert File

```http
POST /convert/
Content-Type: multipart/form-data

file: <file>
```

Converts uploaded files to markdown format.

### 2. Convert URL

```http
POST /convert-url/
Content-Type: application/x-www-form-urlencoded

url=https://example.com
```

Converts web page content to markdown format.

### 3. YouTube Transcript

```http
POST /youtube/
Content-Type: application/x-www-form-urlencoded

url=https://www.youtube.com/watch?v=video_id
```

Returns:

-   Full transcript without timestamps
-   Timestamped transcript
-   Markdown formatted transcript
-   Structured transcript with timing information

## Example Usage

### Python

```python
import requests

# Convert URL
response = requests.post(
    "http://localhost:8000/convert-url/",
    data={"url": "https://example.com"}
)
print(response.json())

# Get YouTube Transcript
response = requests.post(
    "http://localhost:8000/youtube/",
    data={"url": "https://www.youtube.com/watch?v=video_id"}
)
print(response.json())

# Convert File
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/convert/",
        files={"file": f}
    )
print(response.json())
```

### cURL

```bash
# Convert URL
curl -X POST http://localhost:8000/convert-url/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "url=https://example.com"

# Get YouTube Transcript
curl -X POST http://localhost:8000/youtube/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "url=https://www.youtube.com/watch?v=video_id"

# Convert File
curl -X POST http://localhost:8000/convert/ \
  -F "file=@document.pdf"
```

## Dependencies

The project uses several key dependencies which are listed in the requirements.txt file:

```1:18:requirements.txt
fastapi[standard]
uvicorn
pydub
speechrecognition
youtube-transcript-api
python-dotenv
openai
python-multipart
# Add these missing dependencies:
mammoth
markdownify
pandas
pdfminer.six
python-pptx
puremagic
requests
beautifulsoup4
charset-normalizer
```

## Docker Configuration

The project includes a Dockerfile that sets up all necessary dependencies and environment:

```1:54:Dockerfile
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
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade \
    youtube-dl \
    youtube-transcript-api \
    pydub \
    speechrecognition \
    python-dotenv \
    openai \
    python-multipart

# Copy application code
COPY . .

# Expose the port
EXPOSE 8000

# Run using the full path to uvicorn
CMD [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

```

## Error Handling

The API includes comprehensive error handling and will return appropriate HTTP status codes and error messages when issues occur. All endpoints return JSON responses with either the requested data or detailed error information.

## Notes

-   For YouTube transcripts, the API attempts multiple methods to retrieve the transcript, including:
    -   English only
    -   Auto-generated captions
    -   Multiple language variants
    -   Available transcript list
-   Proxy support is available through the PROXY_URL environment variable
-   OpenAI integration is available for enhanced processing capabilities
