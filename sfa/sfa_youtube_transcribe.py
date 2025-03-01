# /// script
# dependencies = [
#   "yt-dlp>=2024.3.10",
#   "transformers>=4.38.2", 
#   "torch>=2.2.1",
#   "rich>=13.7.0"
# ]
# ///

"""
/// Example Usage

# Transcribe a YouTube video
uv run sfa_youtube_transcribe.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Transcribe with custom output file
uv run sfa_youtube_transcribe.py "https://www.youtube.com/watch?v=VIDEO_ID" -o transcript.txt

///
"""

import os
import sys
import argparse
from rich.console import Console
from rich.progress import Progress
import yt_dlp
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

# Initialize rich console
console = Console()

def download_audio(url: str) -> str:
    """Downloads audio from YouTube video."""
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'outtmpl': 'temp_audio.%(ext)s'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        console.log(f"[blue]Downloading audio from: {url}[/blue]")
        ydl.download([url])
        
    return "temp_audio.wav"

def transcribe_audio(audio_path: str) -> str:
    """Transcribes audio file using distil-whisper."""
    
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    console.log("[blue]Loading distil-whisper model...[/blue]")
    
    model_id = "distil-whisper/distil-large-v2"
    
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, 
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
        use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)
    
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=128,
        chunk_length_s=30,
        batch_size=16,
        torch_dtype=torch_dtype,
        device=device,
    )
    
    console.log("[blue]Transcribing audio...[/blue]")
    result = pipe(audio_path, return_timestamps=True)
    
    return result["text"]

def main():
    parser = argparse.ArgumentParser(description="YouTube Video Transcriber")
    parser.add_argument("url", help="YouTube video URL to transcribe")
    parser.add_argument("-o", "--output", help="Output file path", default="transcript.txt")
    args = parser.parse_args()
    
    try:
        # Download audio
        audio_path = download_audio(args.url)
        
        # Transcribe
        transcript = transcribe_audio(audio_path)
        
        # Save transcript
        with open(args.output, "w") as f:
            f.write(transcript)
            
        console.print(f"\n[green]Transcript saved to: {args.output}[/green]")
        
        # Cleanup
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()