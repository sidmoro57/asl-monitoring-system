# Dockerfile for ASL Monitoring System
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create data directory
RUN mkdir -p data

# Expose port
EXPOSE 5000

# Environment variables (can be overridden)
ENV PORT=5000
ENV MONITORING_INTERVAL=5
ENV ALERT_CPU_THRESHOLD=80
ENV ALERT_MEMORY_THRESHOLD=85
ENV ALERT_DISK_THRESHOLD=90

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/api/health')"

# Run the application
CMD ["python", "app.py"]
