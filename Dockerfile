# Build stage
FROM python:3.11.10-slim AS builder

WORKDIR /app

# Prevent Python from writing .pyc files and enable buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file to leverage Docker layer caching
COPY requirements.txt .

# Create wheels for all dependencies to make the final install fast and clean
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final runtime image
FROM python:3.11.10-slim
WORKDIR /app

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create non-root user
ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g ${GROUP_ID} appuser && \
    useradd -u ${USER_ID} -g appuser -m appuser

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install packages AS ROOT
RUN pip install --no-cache /wheels/*

# Copy project code AS ROOT
COPY setup.py .
COPY scripts/ ./scripts/
COPY tests/ ./tests/
COPY config.yml .
COPY main.py .

# Install project as editable package AS ROOT
RUN pip install -e .

# Switch to non-root user for runtime
RUN chown -R appuser:appuser /app
USER appuser

# Health check: verifies the Python process is alive
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import os; exit(0 if os.path.exists('/app/main.py') else 1)"

# Entrypoint
ENTRYPOINT ["python", "main.py"]
