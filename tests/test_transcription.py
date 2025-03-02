import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app_old.routers.transcription import create_router
from app_old.models.transcription import TranscriptionOptions, YoutubeTranscriptionRequest
from tests.utils import TestTranscriptionService

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

def test_transcribe_youtube_valid_url(client):
    """Test transcription of a valid YouTube URL"""
    request = {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "options": {
            "language": "en",
            "return_timestamps": True,
            "chunk_length_s": 30
        }
    }
    response = client.post("/api/v1/transcribe/youtube", json=request)
    
    assert response.status_code == 200
    assert "text" in response.json()
    assert "video_title" in response.json()
    if response.json().get("return_timestamps"):
        assert "segments" in response.json()

def test_transcribe_youtube_invalid_url(client):
    """Test that invalid YouTube URLs are rejected"""
    request = {
        "url": "not-a-valid-url",  # This will fail Pydantic's HttpUrl validation
    }
    response = client.post("/api/v1/transcribe/youtube", json=request)
    assert response.status_code == 422  # Pydantic validation error
    assert "url" in response.json()["detail"][0]["loc"]  # Check that the error is about the URL

def test_transcribe_youtube_nonexistent_video(client):
    """Test handling of nonexistent YouTube videos"""
    request = {
        "url": "https://www.youtube.com/watch?v=nonexistentvideo",
    }
    response = client.post("/api/v1/transcribe/youtube", json=request)
    
    # The TestTranscriptionService should simulate a failure for nonexistent videos
    assert response.status_code == 500
    assert "Failed to transcribe YouTube video" in response.json()["detail"]

def test_transcribe_youtube_with_custom_options(client):
    """Test YouTube transcription with custom options"""
    request = {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "options": {
            "language": "es",  # Spanish
            "return_timestamps": True,
            "chunk_length_s": 60
        }
    }
    response = client.post("/api/v1/transcribe/youtube", json=request)
    
    assert response.status_code == 200
    assert "text" in response.json()
    assert "segments" in response.json()
    assert "video_title" in response.json()

def test_transcribe_youtube_without_options(client):
    """Test YouTube transcription with default options"""
    request = {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }
    response = client.post("/api/v1/transcribe/youtube", json=request)
    
    assert response.status_code == 200
    assert "text" in response.json()
    assert "video_title" in response.json()

def test_transcribe_youtube_short_url(client):
    """Test that YouTube short URLs work"""
    request = {
        "url": "https://youtu.be/dQw4w9WgXcQ"
    }
    response = client.post("/api/v1/transcribe/youtube", json=request)
    
    assert response.status_code == 200
    assert "text" in response.json()
    assert "video_title" in response.json()

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

def test_transcribe_with_options(client):
    """Test transcription with custom options"""
    files = {"file": create_test_audio_file()}
    params = {
        "language": "fr",
        "task": "translate",
        "return_timestamps": "true",
        "chunk_length_s": "60"
    }
    response = client.post("/api/v1/transcribe", files=files, params=params)
    
    assert response.status_code == 200
    assert "text" in response.json()
    assert "segments" in response.json()

def test_transcribe_invalid_options(client):
    """Test transcription with invalid options"""
    files = {"file": create_test_audio_file()}
    params = {
        "chunk_length_s": "0"  # Invalid value
    }
    response = client.post("/api/v1/transcribe", files=files, params=params)
    
    assert response.status_code == 422  # Validation error

@pytest.mark.parametrize("language", ["en", "fr", "es", "de"])
def test_transcribe_different_languages(client, language):
    """Test transcription with different target languages"""
    files = {"file": create_test_audio_file()}
    params = {"language": language}
    response = client.post("/api/v1/transcribe", files=files, params=params)
    
    assert response.status_code == 200
    assert "text" in response.json()
    
@pytest.mark.parametrize("language", ["en", "fr", "es", "de"])
def test_transcribe_youtube_different_languages(client, language):
    """Test YouTube transcription with different target languages"""
    request = {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "options": {
            "language": language
        }
    }
    response = client.post("/api/v1/transcribe/youtube", json=request)
    
    assert response.status_code == 200
    assert "text" in response.json()
    assert "video_title" in response.json()

def test_transcribe_youtube_invalid_options(client):
    """Test YouTube transcription with invalid options"""
    request = {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "options": {
            "chunk_length_s": 0  # Invalid value
        }
    }
    response = client.post("/api/v1/transcribe/youtube", json=request)
    
    assert response.status_code == 422  # Validation error