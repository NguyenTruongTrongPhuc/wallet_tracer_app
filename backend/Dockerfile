# backend/Dockerfile - PHIÊN BẢN CUỐI CÙNG

FROM python:3.11-slim
WORKDIR /app

# Sao chép requirements và cài đặt
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Sao chép code
COPY ./backend /app/backend
ENV PYTHONPATH "${PYTHONPATH}:/app"

# THAY THẾ LỆNH CMD CŨ BẰNG LỆNH NÀY
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]