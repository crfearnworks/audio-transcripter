import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from app.routers.transcription import create_router
from app.services.transcription_service import TestTranscriptionService
import io

@pytest.fixture
def test_app():
    """Create a test instance of the app with the test transcription service"""
    app = FastAPI()
    app.include_router(
        create_router(TestTranscriptionService()), 
        prefix="/api/v1"
    )
    return app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

def create_test_audio_file(size_bytes: int = 1000) -> tuple[str, bytes, str]:
    """Create a test audio file of specified size"""
    return ("test.mp3", b"0" * size_bytes, "audio/mpeg")

def test_transcribe_invalid_file(client):
    """Test that non-audio files are rejected"""
    files = {"file": ("test.txt", b"test content", "text/plain")}
    response = client.post("/api/v1/transcribe", files=files)
    assert response.status_code == 400
    assert "File must be an audio file" in response.json()["detail"]

def test_transcribe_no_file(client):
    """Test that endpoint requires a file"""
    response = client.post("/api/v1/transcribe")
    assert response.status_code == 422  # FastAPI validation error

def test_transcribe_successful(client):
    """Test successful transcription"""
    test_file_size = 1000
    files = {"file": create_test_audio_file(test_file_size)}
    response = client.post("/api/v1/transcribe", files=files)
    
    assert response.status_code == 200
    assert response.json()["text"] == f"Test transcription for file size: {test_file_size} bytes"

@pytest.mark.parametrize("file_type", [
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/mp4",
    "audio/x-m4a",
])
def test_transcribe_accepts_valid_audio_types(client, file_type):
    """Test that various valid audio types are accepted"""
    files = {"file": ("test.audio", b"test content", file_type)}
    response = client.post("/api/v1/transcribe", files=files)
    assert response.status_code == 200
    
def test_transcribe_long_audio(client):
    """Test transcription of audio longer than 30 seconds"""
    # Create a larger file that would represent long audio
    test_file_size = 1_000_000  # 1MB to simulate larger file
    files = {"file": create_test_audio_file(test_file_size)}
    response = client.post("/api/v1/transcribe", files=files)
    
    assert response.status_code == 200
    assert "text" in response.json()