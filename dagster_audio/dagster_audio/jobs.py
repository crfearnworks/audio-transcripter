from dagster import define_asset_job

file_job = define_asset_job(
    name="file_processing_job", 
    selection="*",  # Select all assets
    config={
        "ops": {
            "audio_files_scan": {
                "config": {"folder_path": "/app/data"}
            }
        }
    }
) 