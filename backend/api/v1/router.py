from fastapi import APIRouter
from .endpoints import trace, ai_analysis

api_router = APIRouter()
api_router.include_router(trace.router, prefix="/trace", tags=["Wallet Tracer"])
api_router.include_router(ai_analysis.router, prefix="/ai", tags=["AI Services"])