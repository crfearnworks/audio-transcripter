from dagster import DailyPartitionsDefinition
from datetime import datetime, timedelta

# Create daily partitions starting from 30 days ago
start_date = datetime.now() - timedelta(days=30)
daily_partitions = DailyPartitionsDefinition(
    start_date=start_date.strftime("%Y-%m-%d")
) 