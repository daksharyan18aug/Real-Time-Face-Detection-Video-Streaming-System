# Use slim Python image to keep size small
FROM python:3.11-slim

# Security: run as non-root user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Install system dependencies needed by mediapipe + psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Copy entrypoint script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Start via entrypoint (waits for DB + runs migrations)
CMD ["./entrypoint.sh"]