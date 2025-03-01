from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Union

class TranscriptionOptions(BaseModel):
    language: Optional[str] = Field(
        default=None, 
        description="Source language for transcription (e.g., 'en', 'fr', 'es'). If None, language will be auto-detected"
    )
    return_timestamps: bool = Field(
        default=False,
        description="Whether to return timestamps for each transcribed segment"
    )
    chunk_length_s: int = Field(
        default=30,
        ge=1,
        le=120,
        description="Length of audio chunks to process at a time (in seconds)"
    )

class YoutubeTranscriptionRequest(BaseModel):
    url: HttpUrl = Field(..., description="YouTube video URL to transcribe")
    options: Optional[TranscriptionOptions] = Field(
        default_factory=TranscriptionOptions,
        description="Transcription options"
    )

class TranscriptionResponse(BaseModel):
    text: str
    language: Optional[str] = None
    segments: Optional[List[dict]] = None
    video_title: Optional[str] = None  # Added for YouTube responses