FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY backend/ /app/backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Set Python path
ENV PYTHONPATH=/app

# Expose ports for monitoring
EXPOSE 8000 5555

# Default command (can be overridden in docker-compose)
CMD ["celery", "-A", "backend.tasks", "worker", "--loglevel=info"]
