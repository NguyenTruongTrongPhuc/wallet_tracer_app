# Sử dụng một image Python nhẹ và chính thức
FROM python:3.10-slim

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Sao chép file requirements trước
COPY ./frontend/requirements.txt /app/requirements.txt

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Sao chép toàn bộ thư mục frontend vào bên trong thư mục /app của container
COPY ./frontend /app/frontend

# Lệnh sẽ được chạy khi container khởi động
# Chạy Streamlit thông qua module của Python
CMD ["python", "-m", "streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
