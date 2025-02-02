from fastapi import APIRouter, UploadFile, HTTPException, File
from app.services.transcription_service import TranscriptionService

ALLOWED_AUDIO_TYPES = {
    'audio/mpeg',
    'audio/wav',
    'audio/x-wav',
    'audio/mp4',
    'audio/x-m4a',
}

def create_router(transcription_service: TranscriptionService) -> APIRouter:
    router = APIRouter()

    @router.post("/transcribe")
    async def transcribe_audio(file: UploadFile = File(...)):
        """
        Transcribe an audio file to text.
        
        Args:
            file: Audio file to transcribe
            
        Returns:
            dict: Contains transcribed text
            
        Raises:
            HTTPException: If file is invalid or transcription fails
        """
        if not file.content_type in ALLOWED_AUDIO_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File must be an audio file. Supported types: {', '.join(ALLOWED_AUDIO_TYPES)}"
            )
        
        try:
            text = await transcription_service.transcribe(file)
            return {"text": text}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router