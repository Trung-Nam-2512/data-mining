"""
Ensemble Inference Engine with Soft Voting
"""
import torch
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from app.core.model_loader import load_models
from app.core.preprocessing import preprocessor
from app.constants import ALL_CLASSES, IDX_TO_CLASS
from app.utils.logger import logger
from app.utils.toxicity import toxicity_classifier


class EnsembleEngine:
    """
    Ensemble inference engine using Soft Voting
    Combines predictions from ResNet50, EfficientNet-B0, and MobileNetV3-Large
    """
    
    def __init__(self, device: Optional[torch.device] = None):
        """
        Initialize ensemble engine
        
        Args:
            device: Device to run inference on (auto-detect if None)
        """
        # Auto-detect device
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.device = device
        self.class_names = ALL_CLASSES
        self.num_classes = len(ALL_CLASSES)
        
        # Load all models
        logger.info("Initializing Ensemble Engine...")
        self.models = load_models(device=self.device)
        
        logger.info(f"✅ Ensemble Engine ready with {len(self.models)} models")
    
    def _predict_single_model(
        self, 
        model_name: str, 
        image_tensor: torch.Tensor
    ) -> np.ndarray:
        """
        Get predictions from a single model
        
        Args:
            model_name: Name of the model
            image_tensor: Preprocessed image tensor (1, 3, H, W)
            
        Returns:
            Probability array (num_classes,)
        """
        model = self.models[model_name]
        model.eval()
        
        with torch.no_grad():
            # Forward pass
            outputs = model(image_tensor)
            
            # Apply softmax to get probabilities
            probabilities = F.softmax(outputs, dim=1)
        
        # Convert to numpy and remove batch dimension
        probs_array = probabilities[0].cpu().numpy()
        
        return probs_array
    
    def _get_top_k_predictions(
        self,
        probabilities: np.ndarray,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Get top-k predictions from probability array
        
        Args:
            probabilities: Probability array (num_classes,)
            top_k: Number of top predictions
            
        Returns:
            List of prediction dictionaries
        """
        # Get top-k indices
        top_k_indices = np.argsort(probabilities)[-top_k:][::-1]
        top_k_probs = probabilities[top_k_indices]
        
        predictions = []
        for rank, (idx, prob) in enumerate(zip(top_k_indices, top_k_probs), 1):
            genus = self.class_names[idx]
            toxicity_info = toxicity_classifier.get_toxicity_info(genus)
            
            predictions.append({
                "rank": rank,
                "genus": genus,
                "confidence": float(prob * 100),  # Convert to percentage
                "toxicity": toxicity_info
            })
        
        return predictions
    
    def predict(
        self,
        image_path: str,
        top_k: int = 3,
        return_individual: bool = True
    ) -> Dict:
        """
        Predict mushroom genus using ensemble soft voting
        
        Args:
            image_path: Path to image file
            top_k: Number of top predictions to return
            return_individual: Include individual model predictions
            
        Returns:
            Dictionary with ensemble and individual predictions
        """
        try:
            # Preprocess image
            image_tensor = preprocessor.preprocess(image_path)
            image_tensor = image_tensor.to(self.device)
            
            # Get predictions from each model
            probs_resnet = self._predict_single_model("resnet50", image_tensor)
            probs_efficientnet = self._predict_single_model("efficientnet_b0", image_tensor)
            probs_mobilenet = self._predict_single_model("mobilenet_v3_large", image_tensor)
            
            # Soft Voting: Average probabilities
            ensemble_probs = (probs_resnet + probs_efficientnet + probs_mobilenet) / 3.0
            
            # Get top-k ensemble predictions
            ensemble_predictions = self._get_top_k_predictions(ensemble_probs, top_k)
            
            # Best prediction
            best_pred = ensemble_predictions[0]
            
            # Validation: Check if image is likely a mushroom
            confidence = best_pred["confidence"]
            LOW_CONFIDENCE_THRESHOLD = 40.0  # Below 40% = likely not a mushroom
            VERY_LOW_CONFIDENCE_THRESHOLD = 25.0  # Below 25% = definitely not a mushroom
            
            is_low_confidence = confidence < LOW_CONFIDENCE_THRESHOLD
            is_very_low_confidence = confidence < VERY_LOW_CONFIDENCE_THRESHOLD
            
            # Check if all top predictions have low confidence
            all_low_confidence = all(p["confidence"] < LOW_CONFIDENCE_THRESHOLD for p in ensemble_predictions[:3])
            
            # Build response
            result = {
                "success": True,
                "ensemble_prediction": {
                    "genus": best_pred["genus"],
                    "confidence": confidence,
                    "toxicity": best_pred["toxicity"],
                    "is_low_confidence": is_low_confidence,
                    "is_very_low_confidence": is_very_low_confidence,
                    "warning": None
                },
                "top_predictions": ensemble_predictions,
                "all_probabilities": {
                    self.class_names[i]: float(ensemble_probs[i] * 100)
                    for i in range(self.num_classes)
                },
                "validation": {
                    "is_likely_mushroom": not is_very_low_confidence and not all_low_confidence,
                    "confidence_level": "high" if confidence >= 70 else "medium" if confidence >= 50 else "low" if confidence >= 30 else "very_low",
                    "warning_message": None
                }
            }
            
            # Add warning messages
            if is_very_low_confidence or all_low_confidence:
                result["validation"]["warning_message"] = (
                    "⚠️ Cảnh báo: Độ tin cậy rất thấp. Ảnh này có thể không phải là nấm. "
                    "Vui lòng upload ảnh nấm rõ ràng, đủ sáng và chụp từ nhiều góc độ."
                )
                result["ensemble_prediction"]["warning"] = result["validation"]["warning_message"]
            elif is_low_confidence:
                result["validation"]["warning_message"] = (
                    "⚠️ Lưu ý: Độ tin cậy thấp. Kết quả có thể không chính xác. "
                    "Vui lòng kiểm tra lại ảnh hoặc thử với ảnh khác."
                )
                result["ensemble_prediction"]["warning"] = result["validation"]["warning_message"]
            
            # Add individual model predictions if requested
            if return_individual:
                individual_models = []
                
                # ResNet50
                resnet_top = self._get_top_k_predictions(probs_resnet, top_k=1)[0]
                individual_models.append({
                    "model": "ResNet50",
                    "accuracy": 91.59,  # From training results
                    "genus": resnet_top["genus"],
                    "confidence": resnet_top["confidence"],
                    "toxicity": resnet_top["toxicity"]
                })
                
                # EfficientNet-B0
                efficientnet_top = self._get_top_k_predictions(probs_efficientnet, top_k=1)[0]
                individual_models.append({
                    "model": "EfficientNet-B0",
                    "accuracy": 88.33,
                    "genus": efficientnet_top["genus"],
                    "confidence": efficientnet_top["confidence"],
                    "toxicity": efficientnet_top["toxicity"]
                })
                
                # MobileNetV3-Large
                mobilenet_top = self._get_top_k_predictions(probs_mobilenet, top_k=1)[0]
                individual_models.append({
                    "model": "MobileNetV3-Large",
                    "accuracy": 87.64,
                    "genus": mobilenet_top["genus"],
                    "confidence": mobilenet_top["confidence"],
                    "toxicity": mobilenet_top["toxicity"]
                })
                
                result["individual_models"] = individual_models
            
            logger.info(
                f"Prediction: {best_pred['genus']} "
                f"({best_pred['confidence']:.1f}%) - "
                f"{best_pred['toxicity']['label']}"
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Lỗi khi thực hiện prediction: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def predict_batch(
        self,
        image_paths: List[str],
        top_k: int = 3,
        return_individual: bool = False
    ) -> List[Dict]:
        """
        Predict batch of images
        
        Args:
            image_paths: List of image file paths
            top_k: Number of top predictions per image
            return_individual: Include individual model predictions
            
        Returns:
            List of prediction results
        """
        results = []
        
        for i, image_path in enumerate(image_paths, 1):
            try:
                logger.info(f"Processing image {i}/{len(image_paths)}: {Path(image_path).name}")
                result = self.predict(image_path, top_k, return_individual)
                result["image_path"] = str(image_path)
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing {image_path}: {str(e)}")
                results.append({
                    "success": False,
                    "image_path": str(image_path),
                    "error": f"Lỗi: {str(e)}"
                })
        
        logger.info(f"Batch prediction completed: {len(results)}/{len(image_paths)} successful")
        
        return results
    
    def get_model_info(self) -> Dict:
        """
        Get information about loaded models
        
        Returns:
            Dictionary with model information
        """
        return {
            "ensemble_type": "Soft Voting",
            "num_models": len(self.models),
            "models": [
                {
                    "name": "ResNet50",
                    "accuracy": 91.59,
                    "status": "loaded"
                },
                {
                    "name": "EfficientNet-B0",
                    "accuracy": 88.33,
                    "status": "loaded"
                },
                {
                    "name": "MobileNetV3-Large",
                    "accuracy": 87.64,
                    "status": "loaded"
                }
            ],
            "num_classes": self.num_classes,
            "classes": self.class_names,
            "device": str(self.device)
        }


# Global ensemble engine instance (lazy loaded)
_ensemble_engine: Optional[EnsembleEngine] = None


def get_ensemble_engine() -> EnsembleEngine:
    """
    Get or create global ensemble engine instance (Singleton pattern)
    
    Returns:
        Global ensemble engine
    """
    global _ensemble_engine
    
    if _ensemble_engine is None:
        logger.info("Creating global ensemble engine instance...")
        _ensemble_engine = EnsembleEngine()
    
    return _ensemble_engine


