"""
Model loading utilities with error handling
"""
import torch
from pathlib import Path
from typing import Dict, Optional

from app.core.model_architecture import MushroomClassifier
from app.config import settings
from app.constants import ALL_CLASSES
from app.utils.logger import logger


class ModelLoader:
    """
    Utility class for loading PyTorch models with proper error handling
    """
    
    @staticmethod
    def load_model(
        backbone: str,
        model_path: Path,
        device: torch.device,
        num_classes: int = 11
    ) -> MushroomClassifier:
        """
        Load a single model from checkpoint
        
        Args:
            backbone: Backbone architecture name
            model_path: Path to model checkpoint (.pth file)
            device: Device to load model on (cuda/cpu)
            num_classes: Number of output classes
            
        Returns:
            Loaded model in eval mode
            
        Raises:
            FileNotFoundError: If model file doesn't exist
            RuntimeError: If model loading fails
        """
        # Validate model file exists
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file không tồn tại: {model_path}\n"
                f"Vui lòng đảm bảo file model đã được download và đặt đúng vị trí."
            )
        
        try:
            logger.info(f"Loading model: {backbone} từ {model_path.name}")
            
            # Create model architecture
            model = MushroomClassifier(
                backbone=backbone,
                num_classes=num_classes,
                pretrained=False,  # Không cần pretrained vì sẽ load checkpoint
                freeze_backbone=False
            )
            
            # Load checkpoint
            checkpoint = torch.load(model_path, map_location=device)
            
            # Extract state_dict (handle different checkpoint formats)
            if isinstance(checkpoint, dict):
                state_dict = checkpoint.get('model_state_dict', checkpoint)
            else:
                state_dict = checkpoint
            
            # Handle _orig_mod prefix (from torch.compile)
            # Notebook đã compile models với torch.compile(), cần strip prefix
            if state_dict and len(state_dict) > 0:
                first_key = list(state_dict.keys())[0]
                if first_key.startswith('_orig_mod.'):
                    logger.info(f"Phát hiện _orig_mod prefix, đang strip...")
                    new_state_dict = {}
                    for key, value in state_dict.items():
                        if key.startswith('_orig_mod.'):
                            new_key = key[len('_orig_mod.'):]
                            new_state_dict[new_key] = value
                        else:
                            new_state_dict[key] = value
                    state_dict = new_state_dict
            
            # Load state dict with strict=False to handle minor mismatches
            missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
            
            # Log warnings for missing/unexpected keys
            if missing_keys:
                logger.warning(f"Missing keys ({len(missing_keys)}): {missing_keys[:5]}...")
            if unexpected_keys:
                logger.warning(f"Unexpected keys ({len(unexpected_keys)}): {unexpected_keys[:5]}...")
            
            # Move to device and set to eval mode
            model = model.to(device)
            model.eval()
            
            # Disable dropout and batch norm training behavior
            for module in model.modules():
                if isinstance(module, (torch.nn.Dropout, torch.nn.BatchNorm2d)):
                    module.eval()
            
            logger.info(f"✅ Model {backbone} loaded successfully")
            
            return model
            
        except Exception as e:
            error_msg = f"Lỗi khi load model {backbone}: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    @staticmethod
    def load_all_models(device: Optional[torch.device] = None) -> Dict[str, MushroomClassifier]:
        """
        Load all 3 models for ensemble
        
        Args:
            device: Device to load models on. If None, auto-detect cuda/cpu
            
        Returns:
            Dictionary mapping model names to loaded models
            
        Raises:
            RuntimeError: If any model fails to load
        """
        # Auto-detect device
        if device is None:
            if torch.cuda.is_available() and settings.device.lower() == "cuda":
                device = torch.device("cuda")
                logger.info(f"🚀 Using CUDA: {torch.cuda.get_device_name(0)}")
            else:
                device = torch.device("cpu")
                logger.info("Using CPU")
        
        models = {}
        model_configs = [
            ("resnet50", settings.resnet_model_path),
            ("efficientnet_b0", settings.efficientnet_model_path),
            ("mobilenet_v3_large", settings.mobilenet_model_path)
        ]
        
        for backbone, model_path in model_configs:
            try:
                model = ModelLoader.load_model(
                    backbone=backbone,
                    model_path=model_path,
                    device=device,
                    num_classes=len(ALL_CLASSES)
                )
                models[backbone] = model
                
            except Exception as e:
                logger.error(f"Failed to load {backbone}: {str(e)}")
                raise RuntimeError(
                    f"Không thể load model {backbone}. "
                    f"Vui lòng kiểm tra file model tại: {model_path}"
                )
        
        logger.info(f"✅ All {len(models)} models loaded successfully")
        
        return models


# Convenience function
def load_models(device: Optional[torch.device] = None) -> Dict[str, MushroomClassifier]:
    """
    Convenience function to load all models
    
    Args:
        device: Device to load on (auto-detect if None)
        
    Returns:
        Dictionary of loaded models
    """
    return ModelLoader.load_all_models(device)


