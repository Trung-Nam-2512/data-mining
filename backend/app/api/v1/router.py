"""
API v1 router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import predictions, gradcam, models, health


api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    predictions.router,
    prefix="/predict",
    tags=["Predictions"]
)

api_router.include_router(
    gradcam.router,
    prefix="/gradcam",
    tags=["Grad-CAM"]
)

api_router.include_router(
    models.router,
    prefix="/models",
    tags=["Models"]
)

api_router.include_router(
    health.router,
    tags=["Health & Statistics"]
)


