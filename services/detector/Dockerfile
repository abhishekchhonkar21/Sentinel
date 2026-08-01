# Detector agent service — consumes logs/metrics windows, writes anomaly_events.
# Run: uvicorn detector.main:app --host 0.0.0.0 --port 8001
# PYTHONPATH=services/detector/src:libs/sentinel_core/src

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt libs/ services/detector/ ./
RUN pip install -e libs/sentinel_core && pip install -r requirements.txt
ENV PYTHONPATH=/app/services/detector/src:/app/libs/sentinel_core/src
CMD ["uvicorn", "detector.main:app", "--host", "0.0.0.0", "--port", "8001"]
