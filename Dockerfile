# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for CSV files
RUN mkdir -p /app/data

# Make entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8001

# Run the application with the entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
