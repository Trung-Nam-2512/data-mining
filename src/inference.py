"""
Inference Module for Mushroom Classification
"""
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, List

from src.model import create_model
from src.toxicity import ToxicityClassifier
from src.config import ALL_CLASSES, SOURCE_CLASSES, MODELS_DIR

class MushroomInference:
    """
    Inference class for mushroom classification
    """
    
    def __init__(self, model_path: str = None, device: str = None):
        """
        Initialize inference engine
        
        Args:
            model_path: Path to trained model
            device: Device to run inference on
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        # Tạm thời dùng SOURCE_CLASSES (9 classes) cho Phase 1
        # Sẽ được cập nhật khi load model từ checkpoint
        self.class_names = SOURCE_CLASSES
        self.toxicity_classifier = ToxicityClassifier()
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Load model
        if model_path:
            self.load_model(model_path)
        else:
            self.model = None
    
    def load_model(self, model_path: str):
        """Load trained model"""
        if not Path(model_path).exists():
            # Try to find model in models directory
            model_files = list(MODELS_DIR.glob("best_model_*.pth"))
            if model_files:
                model_path = sorted(model_files)[-1]
                print(f"Using model: {model_path}")
            else:
                raise FileNotFoundError(f"Model not found: {model_path}")
        
        checkpoint = torch.load(model_path, map_location=self.device)
        config = checkpoint.get('config', {})
        
        # Xác định số classes từ config hoặc từ model state dict
        num_classes = config.get('num_classes', None)
        if num_classes is None:
            # Thử đoán từ model state dict (kiểm tra kích thước của classifier)
            # Tìm key có chứa 'classifier' và 'weight'
            for key in checkpoint['model_state_dict'].keys():
                if 'classifier' in key and 'weight' in key:
                    num_classes = checkpoint['model_state_dict'][key].shape[0]
                    break
        
        # Cập nhật class names dựa trên num_classes
        if num_classes == 9:
            # Phase 1: 9 classes từ Source Domain
            self.class_names = SOURCE_CLASSES
        elif num_classes == 11:
            # Phase 2: 11 classes (Source + Target)
            self.class_names = ALL_CLASSES
        else:
            # Fallback: dùng SOURCE_CLASSES nếu không xác định được
            print(f"Warning: Unknown num_classes={num_classes}, using SOURCE_CLASSES (9 classes)")
            self.class_names = SOURCE_CLASSES
        
        # Đảm bảo config có num_classes đúng
        if 'num_classes' not in config or config['num_classes'] != num_classes:
            config['num_classes'] = num_classes
        
        self.model = create_model(**config)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        
        print(f"Model loaded successfully from {model_path}")
        print(f"  Backbone: {config.get('backbone', 'unknown')}")
        print(f"  Number of classes: {num_classes}")
        print(f"  Classes: {', '.join(self.class_names)}")
    
    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """
        Preprocess image for inference
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image tensor
        """
        try:
            image = Image.open(image_path).convert('RGB')
        except Exception as e:
            raise ValueError(f"Error loading image: {e}")
        
        image_tensor = self.transform(image).unsqueeze(0)
        return image_tensor.to(self.device)
    
    def predict(self, image_path: str, top_k: int = 3) -> Dict:
        """
        Predict mushroom genus from image
        
        Args:
            image_path: Path to image file
            top_k: Number of top predictions to return
            
        Returns:
            Dictionary with predictions and toxicity information
        """
        if self.model is None:
            raise ValueError("Model not loaded! Call load_model() first.")
        
        # Preprocess image
        image_tensor = self.preprocess_image(image_path)
        
        # Inference
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = F.softmax(outputs, dim=1)
            probs, indices = torch.topk(probabilities, top_k)
        
        # Get predictions
        predictions = []
        for i in range(top_k):
            idx = indices[0][i].item()
            prob = probs[0][i].item()
            genus = self.class_names[idx]
            
            # Get toxicity information
            toxicity_info = self.toxicity_classifier.get_toxicity_info(genus)
            
            predictions.append({
                "rank": i + 1,
                "genus": genus,
                "confidence": prob * 100,
                "toxicity": toxicity_info
            })
        
        # Best prediction
        best_pred = predictions[0]
        
        return {
            "image_path": image_path,
            "best_prediction": {
                "genus": best_pred["genus"],
                "confidence": best_pred["confidence"],
                "toxicity": best_pred["toxicity"]
            },
            "top_predictions": predictions,
            "all_probabilities": {
                self.class_names[i]: probabilities[0][i].item() * 100
                for i in range(len(self.class_names))
            }
        }
    
    def predict_batch(self, image_paths: List[str]) -> List[Dict]:
        """
        Predict multiple images
        
        Args:
            image_paths: List of image paths
            
        Returns:
            List of prediction dictionaries
        """
        results = []
        for image_path in image_paths:
            try:
                result = self.predict(image_path)
                results.append(result)
            except Exception as e:
                results.append({
                    "image_path": image_path,
                    "error": str(e)
                })
        return results

def main():
    """Example usage"""
    # Initialize inference
    inference = MushroomInference()
    
    # Try to load model
    try:
        inference.load_model(None)  # Will auto-find best model
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please train a model first using: python src/train.py")
        return
    
    # Example prediction (replace with actual image path)
    # result = inference.predict("path/to/image.jpg")
    # print(result)

if __name__ == "__main__":
    main()

