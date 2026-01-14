"""
Pydantic models for prediction endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class ToxicityInfo(BaseModel):
    """Toxicity information"""
    code: str = Field(..., description="Toxicity code: P or E")
    label: str = Field(..., description="Toxicity label in Vietnamese")
    is_poisonous: bool = Field(..., description="Whether the mushroom is poisonous")
    warning: str = Field(..., description="Warning message in Vietnamese")
    color: str = Field(..., description="Color code for UI")


class PredictionItem(BaseModel):
    """Single prediction item"""
    rank: int = Field(..., description="Prediction rank (1-based)")
    genus: str = Field(..., description="Mushroom genus name")
    confidence: float = Field(..., description="Confidence percentage (0-100)")
    toxicity: ToxicityInfo = Field(..., description="Toxicity information")


class EnsemblePrediction(BaseModel):
    """Ensemble prediction result"""
    genus: str = Field(..., description="Predicted genus")
    confidence: float = Field(..., description="Confidence percentage")
    toxicity: ToxicityInfo = Field(..., description="Toxicity information")


class IndividualModelPrediction(BaseModel):
    """Individual model prediction"""
    model: str = Field(..., description="Model name")
    accuracy: float = Field(..., description="Model accuracy from training")
    genus: str = Field(..., description="Predicted genus")
    confidence: float = Field(..., description="Confidence percentage")
    toxicity: ToxicityInfo = Field(..., description="Toxicity information")


class PredictionResponse(BaseModel):
    """Response for single image prediction"""
    success: bool = Field(..., description="Whether prediction was successful")
    image_filename: Optional[str] = Field(None, description="Original image filename")
    ensemble_prediction: EnsemblePrediction = Field(..., description="Ensemble prediction")
    individual_models: Optional[List[IndividualModelPrediction]] = Field(
        None,
        description="Individual model predictions"
    )
    top_predictions: List[PredictionItem] = Field(..., description="Top-k predictions")
    all_probabilities: Dict[str, float] = Field(..., description="All class probabilities")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in ms")
    prediction_id: Optional[str] = Field(None, description="Database record ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "image_filename": "mushroom.jpg",
                "ensemble_prediction": {
                    "genus": "Amanita",
                    "confidence": 95.5,
                    "toxicity": {
                        "code": "P",
                        "label": "Độc",
                        "is_poisonous": True,
                        "warning": "⚠️ CẢNH BÁO: Nấm này là NẤM ĐỘC! Không ăn!",
                        "color": "#ff4444"
                    }
                },
                "individual_models": [
                    {
                        "model": "ResNet50",
                        "accuracy": 91.59,
                        "genus": "Amanita",
                        "confidence": 96.9,
                        "toxicity": {"code": "P", "label": "Độc", "is_poisonous": True, "warning": "...", "color": "#ff4444"}
                    }
                ],
                "top_predictions": [
                    {
                        "rank": 1,
                        "genus": "Amanita",
                        "confidence": 95.5,
                        "toxicity": {"code": "P", "label": "Độc", "is_poisonous": True, "warning": "...", "color": "#ff4444"}
                    }
                ],
                "all_probabilities": {"Amanita": 95.5, "Boletus": 2.1},
                "processing_time_ms": 450.5,
                "prediction_id": "507f1f77bcf86cd799439011"
            }
        }


class BatchPredictionResponse(BaseModel):
    """Response for batch prediction"""
    success: bool = Field(..., description="Whether batch prediction was successful")
    total_images: int = Field(..., description="Total number of images processed")
    successful: int = Field(..., description="Number of successful predictions")
    failed: int = Field(..., description="Number of failed predictions")
    results: List[PredictionResponse] = Field(..., description="Individual prediction results")
    processing_time_ms: Optional[float] = Field(None, description="Total processing time")


class GradCAMResponse(BaseModel):
    """Response for Grad-CAM visualization"""
    success: bool = Field(..., description="Whether Grad-CAM generation was successful")
    image_filename: Optional[str] = Field(None, description="Original image filename")
    model_name: str = Field(..., description="Model name")
    predicted_genus: str = Field(..., description="Predicted genus")
    confidence: float = Field(..., description="Prediction confidence")
    gradcam_image: str = Field(..., description="Base64 encoded Grad-CAM overlay image")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "image_filename": "mushroom.jpg",
                "model_name": "resnet50",
                "predicted_genus": "Amanita",
                "confidence": 96.9,
                "gradcam_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA..."
            }
        }


class ModelInfo(BaseModel):
    """Model information"""
    name: str
    accuracy: float
    status: str


class ModelsInfoResponse(BaseModel):
    """Response for models info endpoint"""
    ensemble_type: str
    num_models: int
    models: List[ModelInfo]
    num_classes: int
    classes: List[str]
    device: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Health status: healthy or unhealthy")
    timestamp: datetime = Field(..., description="Current timestamp")
    models_loaded: bool = Field(..., description="Whether models are loaded")
    database_connected: bool = Field(..., description="Whether database is connected")
    version: str = Field(..., description="API version")


class StatisticsResponse(BaseModel):
    """Statistics response"""
    total_predictions: int = Field(..., description="Total number of predictions")
    poisonous_count: int = Field(..., description="Number of poisonous predictions")
    edible_count: int = Field(..., description="Number of edible predictions")
    avg_confidence: float = Field(..., description="Average confidence")
    top_genera: Optional[List[Dict]] = Field(None, description="Top predicted genera")


