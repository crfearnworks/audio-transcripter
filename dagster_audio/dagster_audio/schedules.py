from dagster import schedule, ScheduleEvaluationContext
from datetime import datetime
from . import assets

@schedule(
    cron_schedule="0 0 * * *",  # Run daily at midnight
    job_name="audio_daily_job",
    execution_timezone="UTC",
)
def daily_audio_schedule(context: ScheduleEvaluationContext):
    """Schedule that runs audio processing jobs daily."""
    return {}