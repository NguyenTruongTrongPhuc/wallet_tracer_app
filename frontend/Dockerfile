# frontend/Dockerfile - PHIÊN BẢN SỬA LỖI MẠNG

FROM python:3.11-slim
WORKDIR /app

# Xóa dòng debug "RUN pip install streamlit-metamask" nếu còn
COPY frontend/requirements.txt .

# Sửa lại lệnh RUN pip install, thêm --index-url
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --index-url https://pypi.org/simple/ -r requirements.txt

COPY ./frontend /app/frontend
ENV PYTHONPATH "${PYTHONPATH}:/app"
EXPOSE 8501
CMD ["streamlit", "run", "/app/frontend/Home.py", "--server.port=8501", "--server.address=0.0.0.0"]