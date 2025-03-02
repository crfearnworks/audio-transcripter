from dagster import Definitions, load_assets_from_modules
from . import schedules
from .assets import file_assets, audio_assets
from .io_managers import filesystem_io_manager
from .resources import AudioTranscriptionResource
from .jobs import file_job

all_assets = load_assets_from_modules([file_assets, audio_assets])

defs = Definitions(
    assets=all_assets,
    schedules=[schedules.daily_audio_schedule],
    jobs=[file_job],
    resources={
        "filesystem": filesystem_io_manager,
        "transcription": AudioTranscriptionResource(
            model_name="distil-whisper/distil-large-v2"  # or distil-medium-v2 for smaller model
        )
    }
)