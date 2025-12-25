"""
Configuration file for Mushroom Classification System
"""
import os
from pathlib import Path

# Base paths - Updated for backend structure
# backend/src/config.py -> backend/ -> project root
BASE_DIR = Path(__file__).parent.parent.parent  # Go up to project root
SOURCE_DATA_DIR = BASE_DIR / "archive" / "Mushrooms"
TARGET_DATA_DIR = BASE_DIR / "Transferdata" / "Transferdata"

# Model paths - relative to project root
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"

# Create directories if they don't exist
MODELS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Class labels - Source Domain (9 classes)
SOURCE_CLASSES = [
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
TARGET_CLASSES = [
    "Exidia",
    "Inocybe"
]

# All classes (11 total)
ALL_CLASSES = SOURCE_CLASSES + TARGET_CLASSES

# Toxicity mapping
TOXICITY_MAPPING = {
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

# Training hyperparameters
TRAIN_CONFIG = {
    "batch_size": 32,
    "num_epochs": 50,
    "learning_rate": 0.001,
    "image_size": (224, 224),
    "num_workers": 4,
    "train_split": 0.7,
    "val_split": 0.15,
    "test_split": 0.15,
    "random_seed": 42
}

# Model configuration
MODEL_CONFIG = {
    "backbone": "resnet50",  # Options: resnet50, efficientnet_b0, mobilenet_v3
    "num_classes": len(ALL_CLASSES),
    "pretrained": True,
    "freeze_backbone": False  # Set to True for transfer learning fine-tuning
}

