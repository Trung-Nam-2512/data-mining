"""
Prediction Endpoints
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from pathlib import Path

from app.services.inference_service import inference_service
from app.schemas.prediction import PredictionResponse, BatchPredictionResponse
from app.utils.file_utils import save_uploaded_file, cleanup_temp_file

router = APIRouter()


@router.post("", response_model=PredictionResponse)
async def predict_mushroom(
    file: UploadFile = File(...),
    top_k: int = 3
):
    """
    Predict mushroom genus from uploaded image
    
    Args:
        file: Image file (JPG, JPEG, PNG)
        top_k: Number of top predictions to return (default: 3, max: 10)
    
    Returns:
        Prediction results with genus, confidence, and toxicity information
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (JPG, JPEG, PNG)"
        )
    
    # Validate top_k
    if top_k < 1 or top_k > 10:
        raise HTTPException(
            status_code=400,
            detail="top_k must be between 1 and 10"
        )
    
    tmp_path = None
    try:
        # Save uploaded file temporarily
        # Note: FastAPI UploadFile needs to be read before saving
        tmp_path = save_uploaded_file(file)
        
        # Verify file exists and is readable
        if not tmp_path.exists():
            raise HTTPException(
                status_code=500,
                detail="Failed to save uploaded file"
            )
        
        # Verify file has content
        if tmp_path.stat().st_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )
        
        # Make prediction
        result = inference_service.predict(str(tmp_path), top_k=top_k)
        
        # Add filename to response
        result["image_filename"] = file.filename
        
        return JSONResponse(content=result)
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error for debugging
        import traceback
        error_detail = str(e)
        error_trace = traceback.format_exc()
        print(f"Prediction endpoint error: {error_detail}")
        print(error_trace)
        
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {error_detail}"
        )
    finally:
        # Clean up temp file
        if tmp_path:
            cleanup_temp_file(tmp_path)


@router.post("/batch", response_model=BatchPredictionResponse)
async def predict_batch(
    files: List[UploadFile] = File(...),
    top_k: int = 3
):
    """
    Predict multiple images in batch
    
    Args:
        files: List of image files (max 10)
        top_k: Number of top predictions per image
    
    Returns:
        List of prediction results
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 files allowed per batch"
        )
    
    results = []
    tmp_paths = []
    
    try:
        for file in files:
            tmp_path = None
            try:
                # Validate file type
                if not file.content_type or not file.content_type.startswith('image/'):
                    results.append({
                        "filename": file.filename or "unknown",
                        "success": False,
                        "error": "File must be an image"
                    })
                    continue
                
                # Save uploaded file temporarily
                tmp_path = save_uploaded_file(file)
                tmp_paths.append(tmp_path)
                
                # Make prediction
                result = inference_service.predict(str(tmp_path), top_k=top_k)
                results.append({
                    "filename": file.filename or "unknown",
                    "success": True,
                    "best_prediction": result["best_prediction"],
                    "top_predictions": result["top_predictions"]
                })
            
            except Exception as e:
                results.append({
                    "filename": file.filename or "unknown",
                    "success": False,
                    "error": str(e)
                })
            # Note: Cleanup will happen at the end
        
        return {
            "success": True,
            "total": len(files),
            "results": results
        }
    
    finally:
        # Clean up all temp files
        for tmp_path in tmp_paths:
            cleanup_temp_file(tmp_path)

