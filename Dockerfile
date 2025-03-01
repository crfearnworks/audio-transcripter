FROM python:3.12-slim

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
COPY README.md .

RUN pip install --no-cache-dir .

COPY app app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]