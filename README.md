# Audio Transcription API

A FastAPI service that provides audio transcription and translation capabilities using Whisper and NLLB models.

## Features

- Audio transcription with language detection
- Support for multiple audio formats (MP3, WAV, M4A, MP4)
- Timestamp support for transcriptions
- Configurable chunk processing for long audio files

## Requirements

- Python 3.12+
- CUDA-compatible GPU (optional, for faster processing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/audio-transcripter.git
cd audio-transcripter
```

2. Install dependencies:
```bash
pip install .
```

## Running the Service

### Using Docker (recommended)

```bash
docker-compose up --build
```

### Without Docker

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### Transcribe Audio
`POST /api/v1/transcribe`

Parameters:
- `file`: Audio file (multipart/form-data)
- `language`: Source language code (optional)
- `return_timestamps`: Return word-level timestamps (optional)
- `chunk_length_s`: Chunk size in seconds (default: 30)

Example:
```bash
curl -X POST "http://localhost:8000/api/v1/transcribe" \
     -H "accept: application/json" \
     -F "file=@audio.mp3" \
     -F "language=en" \
     -F "return_timestamps=true"
```

## Supported Audio Formats

```python:app/routers/transcription.py
startLine: 10
endLine: 16
```

## Development

### Running Tests

```bash
pytest tests/
```

### Project Structure

- `app/`: Main application code
  - `models/`: Pydantic models for request/response
  - `routers/`: API endpoint definitions
  - `services/`: Business logic and ML model integration

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
