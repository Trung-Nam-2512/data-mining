"""
Model information endpoints
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.ensemble import get_ensemble_engine
from app.constants import ALL_CLASSES, TOXICITY_MAPPING
from app.models.prediction import ModelsInfoResponse
from app.utils.logger import logger


router = APIRouter()


@router.get("/info", response_model=ModelsInfoResponse)
async def get_models_info():
    """
    Lấy thông tin về các models đang được sử dụng
    
    Returns thông tin chi tiết về ensemble và từng model.
    """
    try:
        engine = get_ensemble_engine()
        model_info = engine.get_model_info()
        
        return JSONResponse(content=model_info)
        
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Lỗi khi lấy thông tin model: {str(e)}"}
        )


@router.get("/classes")
async def get_classes():
    """
    Lấy danh sách tất cả các classes (genera) và toxicity
    
    Returns danh sách các chi nấm với thông tin độc tính.
    """
    try:
        classes_info = []
        
        for genus in ALL_CLASSES:
            toxicity = TOXICITY_MAPPING.get(genus, "Unknown")
            classes_info.append({
                "genus": genus,
                "toxicity_code": toxicity,
                "toxicity_label": "Độc" if toxicity == "P" else "Ăn được",
                "is_poisonous": toxicity == "P"
            })
        
        return JSONResponse(content={
            "success": True,
            "total_classes": len(ALL_CLASSES),
            "poisonous_count": sum(1 for g in ALL_CLASSES if TOXICITY_MAPPING.get(g) == "P"),
            "edible_count": sum(1 for g in ALL_CLASSES if TOXICITY_MAPPING.get(g) == "E"),
            "classes": classes_info
        })
        
    except Exception as e:
        logger.error(f"Error getting classes: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Lỗi khi lấy danh sách classes: {str(e)}"}
        )


