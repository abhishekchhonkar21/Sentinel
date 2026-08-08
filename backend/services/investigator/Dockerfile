FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt backend/libs/ backend/services/investigator/ ./
RUN pip install -e libs/sentinel_core && pip install -r requirements.txt
ENV PYTHONPATH=/app/services/investigator/src:/app/libs/sentinel_core/src
CMD ["uvicorn", "investigator.main:app", "--host", "0.0.0.0", "--port", "8002"]
