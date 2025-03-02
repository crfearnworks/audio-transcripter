FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and project files
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p /opt/dagster/dagster_home /app/data

# Set environment variables
ENV DAGSTER_HOME=/opt/dagster/dagster_home

# Copy Dagster configuration
COPY dagster.yaml /opt/dagster/dagster_home/

# Expose port
EXPOSE 3000

# Start Dagster
CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]
