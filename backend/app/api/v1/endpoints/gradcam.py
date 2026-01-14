"""
Grad-CAM visualization endpoint
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse

from app.core.ensemble import get_ensemble_engine
from app.core.gradcam import EnsembleGradCAM
from app.utils.file_utils import save_uploaded_file, cleanup_temp_file
from app.models.prediction import GradCAMResponse
from app.utils.logger import logger


router = APIRouter()


@router.post("", response_model=GradCAMResponse)
async def generate_gradcam(
    file: UploadFile = File(..., description="Ảnh nấm (JPG, PNG)"),
    model_name: str = Form(default="resnet50", description="Tên model (resnet50, efficientnet_b0, mobilenet_v3_large)"),
    alpha: float = Form(default=0.5, ge=0.0, le=1.0, description="Độ trong suốt overlay (0-1)")
):
    """
    Tạo Grad-CAM visualization để giải thích prediction
    
    - **file**: File ảnh (JPG, PNG)
    - **model_name**: Tên model để tạo Grad-CAM (resnet50, efficientnet_b0, mobilenet_v3_large)
    - **alpha**: Độ trong suốt của overlay (0-1, mặc định 0.5)
    
    Returns Grad-CAM visualization dạng base64 image.
    """
    tmp_path = None
    
    try:
        # Validate model name
        valid_models = ["resnet50", "efficientnet_b0", "mobilenet_v3_large"]
        if model_name not in valid_models:
            raise HTTPException(
                status_code=400,
                detail=f"Model không hợp lệ. Chọn một trong: {', '.join(valid_models)}"
            )
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File phải là ảnh (JPG, JPEG, PNG)"
            )
        
        # Save uploaded file
        tmp_path = await save_uploaded_file(file)
        
        # Get ensemble engine and models
        engine = get_ensemble_engine()
        
        # Create Grad-CAM generator
        gradcam_generator = EnsembleGradCAM(engine.models, engine.device)
        
        # Generate Grad-CAM for specific model
        gradcam_result = gradcam_generator.gradcams[model_name].generate_base64(
            image_path=str(tmp_path),
            alpha=alpha
        )
        
        # Get prediction for this model
        prediction = engine._predict_single_model(model_name, 
                                                   engine.preprocessor.preprocess(str(tmp_path)).to(engine.device))
        predicted_class = prediction.argmax()
        predicted_genus = engine.class_names[predicted_class]
        confidence = float(prediction[predicted_class] * 100)
        
        result = {
            "success": True,
            "image_filename": file.filename,
            "model_name": model_name,
            "predicted_genus": predicted_genus,
            "confidence": confidence,
            "gradcam_image": gradcam_result
        }
        
        logger.info(f"Grad-CAM generated for {model_name}: {predicted_genus} ({confidence:.1f}%)")
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Grad-CAM error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tạo Grad-CAM: {str(e)}"
        )
    finally:
        # Clean up temp file
        if tmp_path:
            cleanup_temp_file(tmp_path)


@router.post("/all")
async def generate_gradcam_all(
    file: UploadFile = File(..., description="Ảnh nấm (JPG, PNG)"),
    alpha: float = Form(default=0.5, ge=0.0, le=1.0, description="Độ trong suốt overlay")
):
    """
    Tạo Grad-CAM cho tất cả 3 models
    
    - **file**: File ảnh
    - **alpha**: Độ trong suốt overlay
    
    Returns Grad-CAM cho cả 3 models.
    """
    tmp_path = None
    
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
        
        # Create Grad-CAM generator
        gradcam_generator = EnsembleGradCAM(engine.models, engine.device)
        
        # Generate Grad-CAM for all models
        results = gradcam_generator.generate_all(str(tmp_path), alpha=alpha)
        
        # Add filename
        for model_name in results:
            results[model_name]["image_filename"] = file.filename
        
        logger.info(f"Grad-CAM generated for all models: {file.filename}")
        
        return JSONResponse(content={
            "success": True,
            "image_filename": file.filename,
            "results": results
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Grad-CAM all error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tạo Grad-CAM: {str(e)}"
        )
    finally:
        # Clean up temp file
        if tmp_path:
            cleanup_temp_file(tmp_path)


