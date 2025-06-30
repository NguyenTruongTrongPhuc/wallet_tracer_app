import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.v1.router import api_router

print("==============================================")
print("BẮT ĐẦU KIỂM TRA MÔI TRƯỜNG")

current_working_directory = os.getcwd()
print(f"-> Thư mục làm việc hiện tại (CWD): {current_working_directory}")

env_path = Path(current_working_directory) / '.env'
print(f"-> Đang tìm file .env tại đường dẫn: {env_path}")
print(f"-> File .env có tồn tại ở đó không? --- {env_path.exists()} ---")

from backend.core.config import settings
print("-> Cấu hình Pydantic đã tải được:")
print(settings.model_dump())

print("KẾT THÚC KIỂM TRA")
print("==============================================")


logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Wallet Tracer API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to Wallet Tracer API"}