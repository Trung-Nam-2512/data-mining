"""
Model Information Schemas
"""
from pydantic import BaseModel
from typing import List, Optional


class ModelInfoResponse(BaseModel):
    """Model information response schema"""
    backbone: str
    num_classes: int
    classes: List[str]
    device: str
    phase: str


class ClassInfo(BaseModel):
    """Class information schema"""
    genus: str
    toxicity: str
    is_poisonous: bool
    description: str


class ClassesResponse(BaseModel):
    """Classes response schema"""
    classes: List[ClassInfo]
    total: int
    poisonous_count: int
    edible_count: int


class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str
    model_loaded: bool = False
    device: Optional[str] = None
    num_classes: Optional[int] = None
    error: Optional[str] = None

