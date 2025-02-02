import torch
from abc import ABC, abstractmethod
from fastapi import UploadFile
from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoProcessor
import tempfile
import os

class TranscriptionService(ABC):
    @abstractmethod
    async def transcribe(self, file: UploadFile) -> str:
        """Transcribe an audio file to text"""
        pass

class WhisperTranscriptionService(TranscriptionService):
    def __init__(self):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.model_id = "distil-whisper/distil-large-v3"
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id, torch_dtype=self.torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )
        self.model.to(self.device)
        self.processor = AutoProcessor.from_pretrained(self.model_id)
        self.transcriber = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            max_new_tokens=128,
            torch_dtype=self.torch_dtype,
            device=self.device,
            return_timestamps=True
        )

    async def transcribe(self, file: UploadFile) -> str:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            try:
                result = self.transcriber(temp_file.name)
                return result["text"]
            finally:
                os.unlink(temp_file.name)

class TestTranscriptionService(TranscriptionService):
    async def transcribe(self, file: UploadFile) -> str:
        content = await file.read()
        # Simple deterministic "transcription" based on file size
        return f"Test transcription for file size: {len(content)} bytes"