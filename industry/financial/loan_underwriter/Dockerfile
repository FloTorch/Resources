FROM python:3.11-slim

# Set working directory
WORKDIR /app
ENV PYTHONPATH=/app/src

# Install build tools for packages that need compiling (optional, adjust if not needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project metadata first (to leverage Docker layer caching)
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir .

# Copy the rest of your source code
COPY . .

# Expose default backend port
EXPOSE 8000

# Default command (can be overridden by docker-compose)
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0"]