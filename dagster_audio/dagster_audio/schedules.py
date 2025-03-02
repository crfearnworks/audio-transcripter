from dagster import schedule, ScheduleEvaluationContext
from .jobs import file_job

@schedule(
    cron_schedule="0 0 * * *",  # Run daily at midnight
    job=file_job,
    execution_timezone="UTC",
)
def daily_audio_schedule(context: ScheduleEvaluationContext):
    """Schedule that runs audio processing jobs daily."""
    return {}