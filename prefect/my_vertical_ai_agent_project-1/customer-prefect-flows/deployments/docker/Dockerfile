# Dockerfile for Prefect 3.x Customer Flows
FROM python:3.12-slim

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Install the package in development mode
RUN pip install -e .

# Create storage directory
RUN mkdir -p /app/storage

# Create non-root user for security
RUN groupadd -r prefect && useradd -r -g prefect prefect
RUN chown -R prefect:prefect /app
USER prefect

# Expose port for Prefect agent (if needed)
EXPOSE 4200

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import prefect; print('Prefect OK')" || exit 1

# Default command
CMD ["python", "-m", "prefect", "worker", "start", "--pool", "default"]
