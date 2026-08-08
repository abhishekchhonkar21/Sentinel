FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements-fault-injection.txt /app/requirements.txt
COPY backend/libs/sentinel_core /app/libs/sentinel_core
COPY backend/apps/fault_injection /app/apps/fault_injection

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -e /app/libs/sentinel_core

ENV PYTHONPATH=/app/apps/fault_injection/src:/app/libs/sentinel_core/src

EXPOSE 8090

CMD ["uvicorn", "fault_injection.main:app", "--host", "0.0.0.0", "--port", "8090"]
