"""
Inference Service - Business logic for model inference
"""
from typing import Optional
from pathlib import Path
import sys

# Add src to path for legacy code
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.inference import MushroomInference
from app.core.config import TOXICITY_MAPPING


class InferenceService:
    """Service for handling model inference"""
    
    def __init__(self):
        self._engine: Optional[MushroomInference] = None
    
    @property
    def engine(self) -> MushroomInference:
        """Lazy load inference engine"""
        if self._engine is None:
            try:
                self._engine = MushroomInference()
                self._engine.load_model(None)  # Auto-find best model
            except Exception as e:
                # Reset engine on error so it can be retried
                self._engine = None
                raise RuntimeError(f"Failed to initialize inference engine: {str(e)}") from e
        return self._engine
    
    def get_model_info(self) -> dict:
        """Get model information"""
        engine = self.engine
        
        # Get backbone from model attribute or try to infer from config
        backbone = "unknown"
        if hasattr(engine.model, 'backbone_name'):
            backbone = engine.model.backbone_name
        else:
            # Try to get from checkpoint config if available
            # This is a fallback - ideally backbone_name should be set
            try:
                import torch
                model_files = list(Path(__file__).parent.parent.parent.parent / "models").glob("best_model_*.pth")
                if model_files:
                    def get_epoch(filename):
                        try:
                            parts = Path(filename).stem.split('_')
                            epoch_idx = parts.index('epoch') + 1
                            return int(parts[epoch_idx])
                        except (ValueError, IndexError):
                            return 0
                    latest_model = sorted(model_files, key=get_epoch, reverse=True)[0]
                    checkpoint = torch.load(latest_model, map_location='cpu')
                    config = checkpoint.get('config', {})
                    backbone = config.get('backbone', 'unknown')
            except Exception:
                pass
        
        return {
            "backbone": backbone,
            "num_classes": len(engine.class_names),
            "classes": engine.class_names,
            "device": engine.device,
            "phase": "1" if len(engine.class_names) == 9 else "2"
        }
    
    def get_classes_info(self) -> dict:
        """Get all classes with toxicity information"""
        engine = self.engine
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
    
    def predict(self, image_path: str, top_k: int = 3) -> dict:
        """Predict mushroom genus from image"""
        try:
            engine = self.engine
            result = engine.predict(image_path, top_k=top_k)
            
            return {
                "success": True,
                "best_prediction": result["best_prediction"],
                "top_predictions": result["top_predictions"],
                "all_probabilities": result["all_probabilities"]
            }
        except Exception as e:
            # Log the error for debugging
            import traceback
            error_msg = f"Prediction error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)  # In production, use proper logging
            raise RuntimeError(f"Prediction failed: {str(e)}") from e
    
    def get_health_status(self) -> dict:
        """Get health status"""
        try:
            engine = self.engine
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


# Singleton instance
inference_service = InferenceService()

