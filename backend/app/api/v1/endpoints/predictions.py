"""
Prediction endpoints
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List
import time

from app.core.ensemble import get_ensemble_engine
from app.utils.file_utils import save_uploaded_file, cleanup_temp_file
from app.services.database import PredictionHistory
from app.models.prediction import PredictionResponse, BatchPredictionResponse
from app.config import settings
from app.utils.logger import logger


router = APIRouter()


@router.post("", response_model=PredictionResponse)
async def predict_mushroom(
    file: UploadFile = File(..., description="Ảnh nấm (JPG, PNG)"),
    top_k: int = Form(default=3, ge=1, le=10, description="Số lượng predictions trả về")
):
    """
    Nhận diện chi nấm từ ảnh sử dụng Ensemble (Soft Voting)
    
    - **file**: File ảnh (JPG, PNG, tối đa 10MB)
    - **top_k**: Số lượng predictions trả về (1-10, mặc định 3)
    
    Returns prediction với ensemble result và individual model predictions.
    """
    tmp_path = None
    start_time = time.time()
    
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File phải là ảnh (JPG, JPEG, PNG)"
            )
        
        # Save uploaded file
        tmp_path = await save_uploaded_file(file)
        
        # Get ensemble engine
        engine = get_ensemble_engine()
        
        # Make prediction
        result = engine.predict(
            image_path=str(tmp_path),
            top_k=top_k,
            return_individual=True
        )
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Add metadata
        result["image_filename"] = file.filename
        result["processing_time_ms"] = processing_time_ms
        
        # Save to database (non-blocking)
        try:
            prediction_id = await PredictionHistory.save_prediction(
                image_filename=file.filename,
                prediction_result=result,
                processing_time_ms=processing_time_ms
            )
            if prediction_id:
                result["prediction_id"] = prediction_id
        except Exception as db_error:
            logger.warning(f"Failed to save to database: {str(db_error)}")
            # Continue even if DB save fails
        
        logger.info(
            f"Prediction completed: {result['ensemble_prediction']['genus']} "
            f"({result['ensemble_prediction']['confidence']:.1f}%) "
            f"in {processing_time_ms:.0f}ms"
        )
        
        return JSONResponse(content=result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xử lý prediction: {str(e)}"
        )
    finally:
        # Clean up temp file
        if tmp_path:
            cleanup_temp_file(tmp_path)


@router.post("/batch", response_model=BatchPredictionResponse)
async def predict_batch(
    files: List[UploadFile] = File(..., description=f"Danh sách ảnh (tối đa {settings.max_batch_size} ảnh)"),
    top_k: int = Form(default=3, ge=1, le=10, description="Số lượng predictions cho mỗi ảnh")
):
    """
    Nhận diện batch nhiều ảnh nấm cùng lúc
    
    - **files**: Danh sách file ảnh (tối đa 5 ảnh)
    - **top_k**: Số lượng predictions cho mỗi ảnh
    
    Returns predictions cho tất cả các ảnh.
    """
    # Validate batch size
    if len(files) > settings.max_batch_size:
        raise HTTPException(
            status_code=400,
            detail=f"Chỉ được upload tối đa {settings.max_batch_size} ảnh cùng lúc. "
                   f"Bạn đã upload {len(files)} ảnh."
        )
    
    if len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="Vui lòng upload ít nhất 1 ảnh"
        )
    
    start_time = time.time()
    tmp_paths = []
    results = []
    successful = 0
    failed = 0
    
    try:
        # Save all uploaded files
        for file in files:
            try:
                tmp_path = await save_uploaded_file(file)
                tmp_paths.append((tmp_path, file.filename))
            except Exception as e:
                logger.error(f"Error saving file {file.filename}: {str(e)}")
                results.append({
                    "success": False,
                    "image_filename": file.filename,
                    "error": f"Lỗi khi lưu file: {str(e)}"
                })
                failed += 1
        
        # Get ensemble engine
        engine = get_ensemble_engine()
        
        # Process each image
        for tmp_path, filename in tmp_paths:
            try:
                # Make prediction
                result = engine.predict(
                    image_path=str(tmp_path),
                    top_k=top_k,
                    return_individual=False  # Reduce payload for batch
                )
                
                result["image_filename"] = filename
                results.append(result)
                successful += 1
                
                # Save to database (non-blocking)
                try:
                    await PredictionHistory.save_prediction(
                        image_filename=filename,
                        prediction_result=result,
                        processing_time_ms=0  # Not tracking individual times for batch
                    )
                except Exception:
                    pass  # Silently fail DB save for batch
            
            except Exception as e:
                logger.error(f"Error processing {filename}: {str(e)}")
                results.append({
                    "success": False,
                    "image_filename": filename,
                    "error": f"Lỗi khi xử lý ảnh: {str(e)}"
                })
                failed += 1
        
        # Calculate total processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        response = {
            "success": True,
            "total_images": len(files),
            "successful": successful,
            "failed": failed,
            "results": results,
            "processing_time_ms": processing_time_ms
        }
        
        logger.info(
            f"Batch prediction completed: {successful}/{len(files)} successful "
            f"in {processing_time_ms:.0f}ms"
        )
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xử lý batch prediction: {str(e)}"
        )
    finally:
        # Clean up all temp files
        for tmp_path, _ in tmp_paths:
            cleanup_temp_file(tmp_path)
