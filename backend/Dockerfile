# ==============================================================================
# Atlas AI Backend Dockerfile
# Multi-stage lean production image
# ==============================================================================

FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final runtime image
FROM python:3.12-slim AS runtime

WORKDIR /app

# Create unprivileged user for security
RUN useradd -m -u 1000 appuser

# Copy installed wheels and dependencies from builder stage
COPY --chown=appuser:appuser --from=builder /root/.local /home/appuser/.local

# Copy application source code and migrations
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser alembic.ini .
COPY --chown=appuser:appuser entrypoint.sh .
RUN chmod +x entrypoint.sh

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

USER appuser

EXPOSE 8000

CMD ["./entrypoint.sh"]
