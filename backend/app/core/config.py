"""
Application Configuration
"""
from pathlib import Path
from typing import List

# Base paths - relative to project root
BASE_DIR = Path(__file__).parent.parent.parent.parent  # backend/app/core -> project root
SOURCE_DATA_DIR = BASE_DIR / "archive" / "Mushrooms"
TARGET_DATA_DIR = BASE_DIR / "Transferdata" / "Transferdata"
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"

# Create directories if they don't exist
MODELS_DIR.mkdir(exist_ok=True, parents=True)
RESULTS_DIR.mkdir(exist_ok=True, parents=True)

# Class labels - Source Domain (9 classes)
SOURCE_CLASSES: List[str] = [
    "Agaricus",
    "Amanita",
    "Boletus",
    "Cortinarius",
    "Entoloma",
    "Hygrocybe",
    "Lactarius",
    "Russula",
    "Suillus"
]

# Class labels - Target Domain (2 classes)
TARGET_CLASSES: List[str] = [
    "Exidia",
    "Inocybe"
]

# All classes (11 total)
ALL_CLASSES: List[str] = SOURCE_CLASSES + TARGET_CLASSES

# Toxicity mapping
TOXICITY_MAPPING: dict = {
    # Poisonous (P)
    "Amanita": "P",
    "Cortinarius": "P",
    "Entoloma": "P",
    "Inocybe": "P",
    # Edible (E)
    "Agaricus": "E",
    "Boletus": "E",
    "Hygrocybe": "E",
    "Lactarius": "E",
    "Russula": "E",
    "Suillus": "E",
    "Exidia": "E"
}

# API Configuration
API_V1_PREFIX = "/api/v1"
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]










