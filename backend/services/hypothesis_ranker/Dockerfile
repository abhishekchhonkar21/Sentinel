FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt backend/libs/ backend/services/hypothesis_ranker/ ./
RUN pip install -e libs/sentinel_core && pip install -r requirements.txt
ENV PYTHONPATH=/app/services/hypothesis_ranker/src:/app/libs/sentinel_core/src
CMD ["uvicorn", "hypothesis_ranker.main:app", "--host", "0.0.0.0", "--port", "8003"]
