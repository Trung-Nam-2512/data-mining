# Multi-stage build for smaller image size
FROM python:3.10-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Final stage
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY ./app ./app

# Copy models directory (will be overridden by volume mount if provided)
# Note: Models are large (~300MB each), consider downloading them separately
COPY ./models ./models

# Create necessary directories
RUN mkdir -p ./logs ./uploads/temp

# Expose port
EXPOSE 1356

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:1356/ping')"

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "1356"]


