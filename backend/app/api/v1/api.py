"""
API v1 Router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import predictions, model
from app.core.config import API_V1_PREFIX

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    predictions.router,
    prefix="/predict",
    tags=["predictions"]
)

api_router.include_router(
    model.router,
    tags=["model"]
)

