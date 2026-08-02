# Shared Dockerfile for all toy-system microservices.
# Build with: docker build -f apps/toy_system/Dockerfile --build-arg SERVICE=api_gateway --build-arg PORT=8080 .

FROM python:3.11-slim

ARG SERVICE=api_gateway
ARG PORT=8080

WORKDIR /app

# System deps — curl used by Docker healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies (cached layer) — toy-system only; keeps image build fast
COPY requirements-toy-system.txt requirements.txt
COPY libs/sentinel_core /app/libs/sentinel_core
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -e /app/libs/sentinel_core

# Shared toy-system library + target service source
COPY apps/toy_system/common /app/apps/toy_system/common
COPY apps/toy_system/${SERVICE} /app/apps/toy_system/${SERVICE}

# Namespace package: all toy_system/* src dirs on PYTHONPATH merge into one tree.
ENV PYTHONPATH=/app/libs/sentinel_core/src:/app/apps/toy_system/common/src:/app/apps/toy_system/${SERVICE}/src
ENV SERVICE_NAME=${SERVICE}
ENV PORT=${PORT}

EXPOSE ${PORT}

# Module path: toy_system.<service>.main:app
CMD ["sh", "-c", "uvicorn toy_system.${SERVICE_NAME}.main:app --host 0.0.0.0 --port ${PORT}"]
