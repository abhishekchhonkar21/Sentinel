FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt backend/libs/ backend/services/api_gateway/ ./
RUN pip install -e libs/sentinel_core && pip install -r requirements.txt
ENV PYTHONPATH=/app/services/api_gateway/src:/app/libs/sentinel_core/src
CMD ["uvicorn", "api_gateway.main:app", "--host", "0.0.0.0", "--port", "8020"]
