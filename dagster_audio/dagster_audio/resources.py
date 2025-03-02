from dagster import ConfigurableResource
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch

class AudioTranscriptionResource(ConfigurableResource):
    model_name: str = "distil-whisper/distil-large-v2"  # Default to large model, can be changed
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    
    def setup_model(self):
        """Load the Distil-Whisper model and processor."""
        # Load model and processor
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            low_cpu_mem_usage=True,
        )
        model.to(self.device)
        
        processor = AutoProcessor.from_pretrained(self.model_name)
        
        # Create pipeline
        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=30,
            batch_size=16,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device=self.device,
        )
        return pipe
    
    def transcribe_audio(self, audio_path: str) -> dict:
        """Transcribe an audio file using Distil-Whisper."""
        pipe = self.setup_model()
        result = pipe(audio_path)
        return {
            "text": result["text"],
            "language": "en"  # Distil-whisper is English-only
        } 