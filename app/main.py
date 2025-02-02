from fastapi import FastAPI
from app.routers import transcription
from app.services.transcription_service import WhisperTranscriptionService

app = FastAPI(title="Audio Transcription API")

# Use the real implementation in production
app.include_router(
    transcription.create_router(WhisperTranscriptionService()), 
    prefix="/api/v1"
)

@app.get("/")
async def root():
    return {"message": "Audio Transcription API"}