import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- THÊM ĐOẠN CODE NÀY ĐỂ GIẢI QUYẾT VẤN ĐỀ IMPORT ---
# Thao tác này giúp ứng dụng có thể được chạy từ bất kỳ đâu.
# Nó sẽ tìm đường dẫn đến thư mục gốc (wallet-tracer-app) và thêm vào sys.path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# ----------------------------------------------------

# Bây giờ chúng ta sử dụng import tuyệt đối từ thư mục gốc
from backend.api.v1.router import api_router


app = FastAPI(
    title="Crypto Wallet Tracing API",
    description="Một API chuyên sâu để truy vết và phân tích ví Bitcoin.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    # Quan trọng: Cho phép tên miền của frontend được gọi đến API này
    allow_origins=["https://dotoshi.com", "http://dotoshi.com"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Wallet Tracing API!"}
