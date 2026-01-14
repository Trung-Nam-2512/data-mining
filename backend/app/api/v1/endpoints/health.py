"""
Health check and statistics endpoints
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime

from app.core.ensemble import get_ensemble_engine
from app.services.database import Database, PredictionHistory
from app.models.prediction import HealthResponse, StatisticsResponse
from app.utils.logger import logger
from app import __version__


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Kiểm tra trạng thái của API, models và database.
    """
    try:
        # Check if ensemble engine is initialized and has models loaded
        models_loaded = False
        try:
            engine = get_ensemble_engine()
            models_loaded = len(engine.models) > 0
        except Exception:
            models_loaded = False
            
        db_connected = Database.is_connected()
        
        # Status: healthy nếu models loaded, unhealthy nếu không
        status = "healthy" if models_loaded else "unhealthy"
        
        return JSONResponse(content={
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "models_loaded": models_loaded,
            "database_connected": db_connected,
            "version": __version__
        })
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "models_loaded": False,
                "database_connected": False,
                "version": __version__,
                "error": str(e)
            }
        )


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """
    Lấy thống kê về predictions
    
    Returns thống kê từ database về các predictions đã thực hiện.
    """
    try:
        stats = await PredictionHistory.get_statistics()
        
        return JSONResponse(content=stats)
        
    except Exception as e:
        logger.error(f"Statistics error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Lỗi khi lấy thống kê: {str(e)}",
                "total_predictions": 0,
                "poisonous_count": 0,
                "edible_count": 0,
                "avg_confidence": 0
            }
        )


@router.get("/history")
async def get_history(
    limit: int = 10,
    skip: int = 0
):
    """
    Lấy lịch sử predictions
    
    - **limit**: Số lượng records trả về (mặc định 10)
    - **skip**: Số lượng records bỏ qua (cho pagination)
    
    Returns danh sách predictions gần đây.
    """
    try:
        history = await PredictionHistory.get_recent_predictions(limit=limit, skip=skip)
        
        return JSONResponse(content={
            "success": True,
            "count": len(history),
            "limit": limit,
            "skip": skip,
            "predictions": history
        })
        
    except Exception as e:
        logger.error(f"History error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Lỗi khi lấy lịch sử: {str(e)}",
                "predictions": []
            }
        )


