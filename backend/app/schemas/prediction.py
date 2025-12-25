"""
Prediction Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class ToxicityInfo(BaseModel):
    """Toxicity information schema"""
    is_poisonous: bool
    warning: str
    toxicity_description: str


class PredictionItem(BaseModel):
    """Single prediction item"""
    rank: int
    genus: str
    confidence: float = Field(..., ge=0, le=100)
    toxicity: ToxicityInfo


class PredictionResponse(BaseModel):
    """Prediction response schema"""
    success: bool
    image_filename: Optional[str] = None
    best_prediction: PredictionItem
    top_predictions: List[PredictionItem]
    all_probabilities: Dict[str, float]


class BatchPredictionResult(BaseModel):
    """Single result in batch prediction"""
    filename: str
    success: bool
    best_prediction: Optional[PredictionItem] = None
    top_predictions: Optional[List[PredictionItem]] = None
    error: Optional[str] = None


class BatchPredictionResponse(BaseModel):
    """Batch prediction response schema"""
    success: bool
    total: int
    results: List[BatchPredictionResult]

