import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Cấu hình cho API của Blockchain.com (nếu có)
    CLIENT_ID: str = "12f917ae-b4ef-46f7-9c4d-0429a6c2635d"
    CLIENT_SECRET: str = "CyDOT1HKOE0XGC0HBQ8NHSUMmmF9TR8D"
    
    # URL API của bên thứ ba (dùng Blockstream để demo)
    BLOCKCHAIN_API_URL: str = "https://blockstream.info/api"
    
    # Cấu hình cho OpenAI
    OPENAI_API_BASE_URL: str = "https://api.openai.com/v1"

    class Config:
        # Nếu bạn tạo file .env, Pydantic sẽ tự động đọc từ đó
        env_file = ".env"

# Tạo một instance để sử dụng trong toàn bộ ứng dụng
settings = Settings()
