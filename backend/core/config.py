import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CLIENT_ID: str = ""
    CLIENT_SECRET: str = ""
    
    BLOCKCHAIN_API_URL: str = "https://blockstream.info/api"
    
    OPENAI_API_BASE_URL: str = "https://api.openai.com/v1"
    
    OPENAI_API_KEY: str = ""
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    SESSION_SECRET_KEY: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()