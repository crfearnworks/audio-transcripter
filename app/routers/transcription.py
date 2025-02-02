from fastapi import APIRouter, UploadFile, HTTPException, File, Depends
from app.services.transcription_service import TranscriptionService
from app.models.transcription import (
    TranscriptionOptions, 
    TranscriptionResponse,
)

ALLOWED_AUDIO_TYPES = {
    'audio/mpeg',
    'audio/wav',
    'audio/x-wav',
    'audio/mp4',
    'audio/x-m4a',
}

def create_router(transcription_service: TranscriptionService) -> APIRouter:
    router = APIRouter()

    @router.post("/transcribe", response_model=TranscriptionResponse)
    async def transcribe_audio(
        file: UploadFile = File(...),
        options: TranscriptionOptions = Depends()
    ):
        """
        Transcribe an audio file to text in its original language.
        """
        if not file.content_type in ALLOWED_AUDIO_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File must be an audio file. Supported types: {', '.join(ALLOWED_AUDIO_TYPES)}"
            )
        
        try:
            result = await transcription_service.transcribe(file, options)
            
            # Handle different response formats
            if isinstance(result, str):
                return TranscriptionResponse(text=result)
            elif isinstance(result, dict):
                if "text" not in result:
                    result = {"text": " ".join(chunk["text"] for chunk in result)}
                return TranscriptionResponse(**result)
            elif isinstance(result, list):
                text = " ".join(chunk["text"] for chunk in result)
                return TranscriptionResponse(text=text, segments=result)
            
            raise HTTPException(
                status_code=500, 
                detail="Unexpected response format from transcription service"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router