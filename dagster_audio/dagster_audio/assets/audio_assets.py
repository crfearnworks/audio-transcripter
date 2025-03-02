from dagster import asset, AssetIn
import pandas as pd
from typing import Dict
from ..partitions import daily_partitions

@asset(
    group_name="audio",
    partitions_def=daily_partitions,
    ins={
        "audio_files": AssetIn("audio_files_scan")
    },
    description="Transcribes audio files and returns results"
)
def audio_transcriptions(
    context,
    audio_files: pd.DataFrame,
    transcription: AudioTranscriptionResource,
) -> Dict[str, dict]:
    """Process audio files for the given partition."""
    partition_date = context.partition_key
    # Filter files by date
    day_files = audio_files[
        audio_files['modified_time'].dt.strftime('%Y-%m-%d') == partition_date
    ]
    results = {}
    
    for _, file_info in day_files.iterrows():
        try:
            result = transcription.transcribe(file_info['path'])
            results[file_info['filename']] = {
                'text': result['text'],
                'segments': result.get('segments', []),
                'file_info': file_info.to_dict()
            }
            context.log.info(f"Transcribed: {file_info['filename']}")
        except Exception as e:
            context.log.error(f"Failed to transcribe {file_info['filename']}: {str(e)}")
            continue
    
    return results 