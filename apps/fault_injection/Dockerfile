FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt libs/ apps/fault_injection/ ./
RUN pip install -e libs/sentinel_core && pip install -r requirements.txt
ENV PYTHONPATH=/app/apps/fault_injection/src:/app/libs/sentinel_core/src
CMD ["uvicorn", "fault_injection.main:app", "--host", "0.0.0.0", "--port", "8030"]
