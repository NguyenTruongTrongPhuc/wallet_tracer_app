# Sử dụng một image Python nhẹ và chính thức
FROM python:3.10-slim

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Sao chép file requirements trước để tận dụng cache của Docker
COPY ./backend/requirements.txt /app/requirements.txt

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Sao chép toàn bộ thư mục backend vào bên trong thư mục /app của container
# Bây giờ, cấu trúc sẽ là /app/backend/...
COPY ./backend /app/backend

# Lệnh sẽ được chạy khi container khởi động
# Chạy Gunicorn thông qua module của Python
CMD ["python", "-m", "gunicorn", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "backend.main:app"]
