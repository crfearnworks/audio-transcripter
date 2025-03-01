# /// script
# dependencies = [
#   "yt-dlp>=2024.3.10",
#   "pydub>=0.25.1",
#   "openai-whisper>=20231117",
#   "phonemizer>=3.2.1",
# ]
# ///

"""
/// Example Usage

# Process a YouTube video's audio into phonemes
uv run sfa_youtube_phonemes.py --url "https://youtube.com/watch?v=example" --output "output.txt"

# Customize chunk duration (in seconds)
uv run sfa_youtube_phonemes.py --url "https://youtube.com/watch?v=example" --chunk-duration 45

# Use specific language for phonemization
uv run sfa_youtube_phonemes.py --url "https://youtube.com/watch?v=example" --language "en-us"

///
"""

import os
import argparse
from typing import List
import yt_dlp
from pydub import AudioSegment
import whisper
from phonemizer import phonemize
from rich.console import Console
from rich.progress import Progress

# Initialize rich console for nice output
console = Console()

def download_audio(url: str, output_path: str = "temp_audio.mp3") -> str:
    """Download audio from YouTube video."""
    console.log(f"Downloading audio from: {url}")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return output_path

def chunk_audio(audio_path: str, chunk_duration: int = 30) -> List[str]:
    """Split audio file into chunks of specified duration."""
    console.log(f"Chunking audio into {chunk_duration}-second segments")
    
    audio = AudioSegment.from_mp3(audio_path)
    chunk_length_ms = chunk_duration * 1000
    chunks = []
    
    with Progress() as progress:
        task = progress.add_task("Chunking audio...", total=len(audio))
        
        for i, chunk_start in enumerate(range(0, len(audio), chunk_length_ms)):
            chunk = audio[chunk_start:chunk_start + chunk_length_ms]
            chunk_path = f"chunk_{i}.mp3"
            chunk.export(chunk_path, format="mp3")
            chunks.append(chunk_path)
            progress.update(task, advance=chunk_length_ms)
    
    return chunks

def transcribe_chunks(chunk_paths: List[str], model_name: str = "base") -> List[str]:
    """Transcribe audio chunks using Whisper."""
    console.log("Transcribing audio chunks")
    
    model = whisper.load_model(model_name)
    transcriptions = []
    
    with Progress() as progress:
        task = progress.add_task("Transcribing...", total=len(chunk_paths))
        
        for chunk_path in chunk_paths:
            result = model.transcribe(chunk_path)
            transcriptions.append(result["text"])
            progress.update(task, advance=1)
    
    return transcriptions

def generate_phonemes(texts: List[str], language: str = "en-us") -> List[str]:
    """Convert transcribed text to phonemes."""
    console.log("Generating phonemes")
    
    phonemes = []
    with Progress() as progress:
        task = progress.add_task("Generating phonemes...", total=len(texts))
        
        for text in texts:
            phoneme_text = phonemize(
                text,
                language=language,
                backend="espeak",
                strip=True
            )
            phonemes.append(phoneme_text)
            progress.update(task, advance=1)
    
    return phonemes

def cleanup_temp_files(chunk_paths: List[str], audio_path: str):
    """Remove temporary files."""
    for chunk_path in chunk_paths:
        if os.path.exists(chunk_path):
            os.remove(chunk_path)
    
    if os.path.exists(audio_path):
        os.remove(audio_path)

def main():
    parser = argparse.ArgumentParser(description="Process YouTube video audio into phonemes")
    parser.add_argument("--url", required=True, help="YouTube video URL")
    parser.add_argument("--output", default="phonemes.txt", help="Output file path")
    parser.add_argument("--chunk-duration", type=int, default=30, help="Duration of audio chunks in seconds")
    parser.add_argument("--language", default="en-us", help="Language for phonemization")
    parser.add_argument("--model", default="base", help="Whisper model to use (tiny, base, small, medium, large)")
    args = parser.parse_args()

    try:
        # Download audio
        audio_path = download_audio(args.url)
        
        # Split into chunks
        chunk_paths = chunk_audio(audio_path, args.chunk_duration)
        
        # Transcribe chunks
        transcriptions = transcribe_chunks(chunk_paths, args.model)
        
        # Generate phonemes
        phonemes = generate_phonemes(transcriptions, args.language)
        
        # Save results
        with open(args.output, "w", encoding="utf-8") as f:
            for i, (text, phoneme) in enumerate(zip(transcriptions, phonemes)):
                f.write(f"Chunk {i+1}:\n")
                f.write(f"Text: {text}\n")
                f.write(f"Phonemes: {phoneme}\n\n")
        
        console.log(f"[green]Results saved to {args.output}[/green]")
        
    finally:
        # Cleanup
        cleanup_temp_files(chunk_paths, audio_path)

if __name__ == "__main__":
    main()