from dagster import asset, Config, AssetIn, RetryPolicy
import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Any

class FolderScanConfig(Config):
    folder_path: str = "/app/data"  # Default path
    include_extensions: List[str] = ["mp3", "wav", "m4a", "mp4"]  # Default to audio files
    exclude_hidden: bool = True
    min_file_size: int = 1024  # Minimum file size in bytes

@asset(
    group_name="files",  # Add group for better organization
    description="Scans folder for audio files and returns metadata",
    io_manager_key="filesystem",  # Specify storage
    retry_policy=RetryPolicy(
        max_retries=3,
        delay=30,
    )
)
def audio_files_scan(context, config: FolderScanConfig) -> pd.DataFrame:
    """
    Scans a folder recursively and returns file information as a DataFrame.
    
    Returns a DataFrame with columns:
    - filename: Name of the file
    - path: Full path to the file
    - size_bytes: Size of file in bytes
    - extension: File extension
    - modified_time: Last modification timestamp
    """
    files_data = []
    
    if not os.path.exists(config.folder_path):
        context.log.error(f"Folder path does not exist: {config.folder_path}")
        return pd.DataFrame()
    
    for root, dirs, files in os.walk(config.folder_path):
        # Skip hidden directories if configured
        if config.exclude_hidden:
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
        for filename in files:
            # Skip hidden files if configured
            if config.exclude_hidden and filename.startswith('.'):
                continue
                
            # Check file extension if filter is specified
            if config.include_extensions:
                ext = os.path.splitext(filename)[1].lower()
                if ext and ext[1:] not in config.include_extensions:  # Remove the dot
                    continue
            
            file_path = os.path.join(root, filename)
            
            try:
                file_stats = os.stat(file_path)
                
                if file_stats.st_size < config.min_file_size:
                    continue
                
                file_info = {
                    'filename': filename,
                    'path': file_path,
                    'size_bytes': file_stats.st_size,
                    'extension': os.path.splitext(filename)[1].lower(),
                    'modified_time': datetime.fromtimestamp(file_stats.st_mtime)
                }
                
                files_data.append(file_info)
            except (FileNotFoundError, PermissionError) as e:
                # Handle errors gracefully
                continue
    
    # Create and return the DataFrame
    return pd.DataFrame(files_data)