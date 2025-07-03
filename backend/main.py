import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.v1.router import api_router
from backend.core.config import settings
from starlette.middleware.session import SessionMiddleware

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Wallet Tracer API", version="1.0")

app.add_middleware(
    SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY
)

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