from typing import Union, Dict
from fastapi import UploadFile
from app.services.transcription_service import TranscriptionService
from app.models.transcription import TranscriptionOptions

class TestTranscriptionService(TranscriptionService):
    async def transcribe(
        self, 
        source: Union[UploadFile, str], 
        options: TranscriptionOptions,
        is_youtube: bool = False
    ) -> Dict:
        """Mock transcription service that returns test data"""
        if is_youtube:
            # Simulate YouTube video transcription
            if not isinstance(source, str):
                raise ValueError("YouTube source must be a string URL")
            
            # Simulate failure for nonexistent video
            if "nonexistentvideo" in source:
                raise RuntimeError("Video unavailable")

            return {
                "text": f"Test transcription for YouTube video: {source}",
                "language": options.language or "en",
                "video_title": "Test Video Title",
                "segments": [
                    {"start": 0, "end": 1, "text": "Test segment"}
                ] if options.return_timestamps else None
            }
        else:
            # Existing file upload logic
            content = await source.read()
            result = {
                "text": f"Test transcription for file size: {len(content)} bytes",
                "language": options.language or "en",
            }
            if options.return_timestamps:
                result["segments"] = [
                    {"start": 0, "end": 1, "text": "Test segment"}
                ]
            return result