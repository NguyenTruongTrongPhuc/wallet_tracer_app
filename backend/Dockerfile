FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./backend /app/backend

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "backend.main:app", "--bind", "0.0.0.0:8000", "--timeout", "300"]
