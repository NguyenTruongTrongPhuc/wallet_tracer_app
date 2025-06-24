from fastapi import APIRouter
# Sử dụng import tuyệt đối
from backend.api.v1.endpoints import trace

api_router = APIRouter()
api_router.include_router(trace.router, prefix="/tracing", tags=["Tracing"])
