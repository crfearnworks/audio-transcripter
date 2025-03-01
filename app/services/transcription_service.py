import yt_dlp
from pathlib import Path
import torch
from abc import ABC, abstractmethod
from fastapi import UploadFile
from app.models.transcription import TranscriptionOptions
from typing import Union, Dict, List, Optional
from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoProcessor
import tempfile
import os

class TranscriptionService(ABC):
    @abstractmethod
    async def transcribe(
        self, 
        source: Union[UploadFile, str], 
        options: TranscriptionOptions,
        is_youtube: bool = False
    ) -> Union[str, Dict, List]:
        """Transcribe an audio file or YouTube video to text"""
        pass

class WhisperTranscriptionService(TranscriptionService):
    def __init__(self):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.model_id = "distil-whisper/distil-large-v3"
        
        # Initialize model for transcription
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id, 
            torch_dtype=self.torch_dtype, 
            low_cpu_mem_usage=True, 
            use_safetensors=True
        )
        self.model.to(self.device)
        self.processor = AutoProcessor.from_pretrained(self.model_id)
        
        # Pipeline for transcription
        self.transcriber = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            max_new_tokens=128,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )

    async def _download_youtube_audio(self, url: str) -> tuple[str, str]:
        """Download audio from YouTube video and return path to audio file and video title"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info['title']
            audio_path = Path(f"{video_title}.mp3")
            return str(audio_path), video_title

    async def transcribe(
        self, 
        source: Union[UploadFile, str], 
        options: TranscriptionOptions,
        is_youtube: bool = False
    ) -> Union[str, Dict, List]:
        try:
            if is_youtube:
                audio_path, video_title = await self._download_youtube_audio(source)
                try:
                    result = self.transcriber(
                        audio_path,
                        chunk_length_s=options.chunk_length_s,
                        return_timestamps=options.return_timestamps,
                        generate_kwargs={"language": options.language} if options.language else {}
                    )
                    if isinstance(result, dict):
                        result['video_title'] = video_title
                    return result
                finally:
                    # Clean up downloaded file
                    Path(audio_path).unlink(missing_ok=True)
            else:
                # Existing file upload logic
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    content = await source.read()
                    temp_file.write(content)
                    temp_file.flush()
                    
                    try:
                        return self.transcriber(
                            temp_file.name,
                            chunk_length_s=options.chunk_length_s,
                            return_timestamps=options.return_timestamps,
                            generate_kwargs={"language": options.language} if options.language else {}
                        )
                    finally:
                        os.unlink(temp_file.name)
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {str(e)}")

