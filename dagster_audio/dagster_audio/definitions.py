from dagster import Definitions, load_assets_from_modules, define_asset_job

from dagster_audio import schedules
from dagster_audio.assets import file_assets

all_assets = load_assets_from_modules([file_assets])

# Define jobs for different asset groups
file_job = define_asset_job(
    name="file_processing_job", 
    selection="files/*"  # Select assets in the 'files' group
)

defs = Definitions(
    assets=all_assets,
    schedules=[schedules.daily_audio_schedule],
    jobs=[file_job],
)