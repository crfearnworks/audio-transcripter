FROM python:3.12-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies first (for better caching)
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy the dagster implementation
COPY dagster_audio/ ./dagster_audio/
RUN pip install -e "./dagster_audio[dev]"

# Set environment variables
ENV PYTHONPATH=/app
ENV DAGSTER_HOME=/opt/dagster/dagster_home

# Create dagster home directory and copy configuration
RUN mkdir -p /opt/dagster/dagster_home
COPY workspace.yaml /opt/dagster/dagster_home/
COPY dagster.yaml /opt/dagster/dagster_home/

# Expose ports for FastAPI and Dagster
EXPOSE 3000

ENTRYPOINT ["dagster-webserver", "-h", "0.0.0.0", "-p", "3000"]
