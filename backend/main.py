"""
FastAPI Backend for Mushroom Classification System
RESTful API for mushroom genus recognition and toxicity detection
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import uvicorn
import tempfile
import shutil

from src.inference import MushroomInference
from src.config import SOURCE_CLASSES, ALL_CLASSES, TOXICITY_MAPPING

# Initialize FastAPI app
app = FastAPI(
    title="Mushroom Classification API",
    description="RESTful API for mushroom genus recognition and toxicity detection using Deep Learning",
    version="1.0.0"
)

# CORS middleware để frontend có thể gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev server ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global inference engine (lazy loading)
_inference_engine: Optional[MushroomInference] = None


def get_inference_engine() -> MushroomInference:
    """Lazy load inference engine"""
    global _inference_engine
    if _inference_engine is None:
        _inference_engine = MushroomInference()
        try:
            _inference_engine.load_model(None)  # Auto-find best model
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load model: {str(e)}"
            )
    return _inference_engine


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Mushroom Classification API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "model_info": "/api/v1/model/info",
            "classes": "/api/v1/classes",
            "predict": "/api/v1/predict (POST)",
            "predict_batch": "/api/v1/predict/batch (POST)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        engine = get_inference_engine()
        return {
            "status": "healthy",
            "model_loaded": engine.model is not None,
            "device": engine.device,
            "num_classes": len(engine.class_names)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/api/v1/model/info")
async def get_model_info():
    """Get model information"""
    try:
        engine = get_inference_engine()
        return {
            "backbone": engine.model.backbone_name if hasattr(engine.model, 'backbone_name') else "unknown",
            "num_classes": len(engine.class_names),
            "classes": engine.class_names,
            "device": engine.device,
            "phase": "1" if len(engine.class_names) == 9 else "2"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/classes")
async def get_classes():
    """Get all available mushroom classes and toxicity information"""
    try:
        engine = get_inference_engine()
        classes_info = []
        
        for genus in engine.class_names:
            toxicity = TOXICITY_MAPPING.get(genus, "Unknown")
            classes_info.append({
                "genus": genus,
                "toxicity": toxicity,
                "is_poisonous": toxicity == "P",
                "description": "Poisonous" if toxicity == "P" else "Edible"
            })
        
        return {
            "classes": classes_info,
            "total": len(classes_info),
            "poisonous_count": sum(1 for c in classes_info if c["is_poisonous"]),
            "edible_count": sum(1 for c in classes_info if not c["is_poisonous"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/predict")
async def predict_mushroom(file: UploadFile = File(...), top_k: int = 3):
    """
    Predict mushroom genus from uploaded image
    
    Args:
        file: Image file (JPG, JPEG, PNG)
        top_k: Number of top predictions to return (default: 3)
    
    Returns:
        Prediction results with genus, confidence, and toxicity information
    """
    # Validate file type
    if not file.content_type.startswith('image/'):
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
    
    try:
        engine = get_inference_engine()
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            # Make prediction
            result = engine.predict(tmp_path, top_k=top_k)
            
            # Format response
            response = {
                "success": True,
                "image_filename": file.filename,
                "best_prediction": result["best_prediction"],
                "top_predictions": result["top_predictions"],
                "all_probabilities": result["all_probabilities"]
            }
            
            return JSONResponse(content=response)
        
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/api/v1/predict/batch")
async def predict_batch(files: List[UploadFile] = File(...), top_k: int = 3):
    """
    Predict multiple images in batch
    
    Args:
        files: List of image files
        top_k: Number of top predictions per image
    
    Returns:
        List of prediction results
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 files allowed per batch"
        )
    
    try:
        engine = get_inference_engine()
        results = []
        
        for file in files:
            if not file.content_type.startswith('image/'):
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": "File must be an image"
                })
                continue
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
                shutil.copyfileobj(file.file, tmp_file)
                tmp_path = tmp_file.name
            
            try:
                # Make prediction
                result = engine.predict(tmp_path, top_k=top_k)
                results.append({
                    "filename": file.filename,
                    "success": True,
                    "best_prediction": result["best_prediction"],
                    "top_predictions": result["top_predictions"]
                })
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": str(e)
                })
            finally:
                Path(tmp_path).unlink(missing_ok=True)
        
        return {
            "success": True,
            "total": len(files),
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction failed: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

