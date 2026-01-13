"""
Model Information Endpoints
"""
from fastapi import APIRouter, HTTPException

from app.services.inference_service import inference_service
from app.schemas.model import ModelInfoResponse, ClassesResponse, HealthResponse

router = APIRouter()


@router.get("/model/info", response_model=ModelInfoResponse)
async def get_model_info():
    """Get model information"""
    try:
        info = inference_service.get_model_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classes", response_model=ClassesResponse)
async def get_classes():
    """Get all available mushroom classes and toxicity information"""
    try:
        classes_info = inference_service.get_classes_info()
        return classes_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return inference_service.get_health_status()








