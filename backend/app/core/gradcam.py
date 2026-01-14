"""
Grad-CAM visualization for model interpretability
"""
import torch
import torch.nn.functional as F
import numpy as np
import cv2
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional
import io
import base64

from app.core.preprocessing import preprocessor
from app.utils.logger import logger


class GradCAM:
    """
    Grad-CAM (Gradient-weighted Class Activation Mapping)
    Visualizes which regions of image the model focuses on
    """
    
    def __init__(self, model, backbone_name: str, device: torch.device):
        """
        Initialize Grad-CAM
        
        Args:
            model: PyTorch model
            backbone_name: Name of backbone architecture
            device: Device to run on
        """
        self.model = model
        self.backbone_name = backbone_name
        self.device = device
        
        # Get target layer based on backbone
        self.target_layer = self._get_target_layer()
        
        # Storage for gradients and activations
        self.gradients = []
        self.activations = []
        
        logger.debug(f"Grad-CAM initialized for {backbone_name}")
    
    def _get_target_layer(self):
        """Get the target layer for Grad-CAM based on backbone"""
        if 'resnet' in self.backbone_name:
            # ResNet: last layer of layer4
            return self.model.backbone.layer4[-1]
        elif 'efficientnet' in self.backbone_name:
            # EfficientNet: last feature layer
            return self.model.backbone.features[-1]
        elif 'mobilenet' in self.backbone_name:
            # MobileNetV3: last feature layer
            return self.model.backbone.features[-1]
        else:
            raise ValueError(f"Unsupported backbone for Grad-CAM: {self.backbone_name}")
    
    def _backward_hook(self, module, grad_input, grad_output):
        """Hook to capture gradients"""
        self.gradients.append(grad_output[0])
    
    def _forward_hook(self, module, input, output):
        """Hook to capture activations"""
        self.activations.append(output)
    
    def generate(
        self,
        image_path: str,
        target_class: Optional[int] = None,
        alpha: float = 0.5
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate Grad-CAM visualization
        
        Args:
            image_path: Path to input image
            target_class: Target class index (None = use predicted class)
            alpha: Overlay transparency (0-1)
            
        Returns:
            Tuple of (original_image, heatmap, overlay)
        """
        try:
            # Clear previous hooks
            self.gradients = []
            self.activations = []
            
            # Register hooks
            backward_handle = self.target_layer.register_full_backward_hook(self._backward_hook)
            forward_handle = self.target_layer.register_forward_hook(self._forward_hook)
            
            # Load and preprocess image
            image_tensor = preprocessor.preprocess(image_path).to(self.device)
            
            # Load original image for visualization
            original_image = Image.open(image_path).convert('RGB')
            original_image = np.array(original_image.resize((224, 224)))
            
            # Enable gradients
            self.model.eval()
            image_tensor.requires_grad = True
            
            # Forward pass
            output = self.model(image_tensor)
            
            # Get target class
            if target_class is None:
                target_class = output.argmax(dim=1).item()
            
            # Backward pass
            self.model.zero_grad()
            one_hot = torch.zeros_like(output)
            one_hot[0, target_class] = 1
            output.backward(gradient=one_hot)
            
            # Remove hooks
            backward_handle.remove()
            forward_handle.remove()
            
            # Compute Grad-CAM
            gradients = self.gradients[0]
            activations = self.activations[0]
            
            # Global average pooling of gradients
            weights = gradients.mean(dim=(2, 3), keepdim=True)
            
            # Weighted combination of activation maps
            cam = (weights * activations).sum(dim=1, keepdim=True)
            
            # ReLU
            cam = F.relu(cam)
            
            # Convert to numpy
            cam = cam.squeeze().cpu().detach().numpy()
            
            # Normalize to [0, 1]
            if cam.max() > 0:
                cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
            
            # Resize to original image size (224x224)
            cam_resized = cv2.resize(cam, (224, 224))
            
            # Apply colormap (COLORMAP_JET)
            heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
            heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
            
            # Create overlay
            overlay = np.uint8(original_image * (1 - alpha) + heatmap * alpha)
            
            logger.debug(f"Grad-CAM generated for class {target_class}")
            
            return original_image, heatmap, overlay
            
        except Exception as e:
            error_msg = f"Lỗi khi tạo Grad-CAM: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def generate_base64(
        self,
        image_path: str,
        target_class: Optional[int] = None,
        alpha: float = 0.5
    ) -> str:
        """
        Generate Grad-CAM and return as base64 encoded image
        
        Args:
            image_path: Path to input image
            target_class: Target class index
            alpha: Overlay transparency
            
        Returns:
            Base64 encoded PNG image
        """
        _, _, overlay = self.generate(image_path, target_class, alpha)
        
        # Convert to PIL Image
        overlay_image = Image.fromarray(overlay)
        
        # Convert to base64
        buffer = io.BytesIO()
        overlay_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        base64_str = base64.b64encode(buffer.read()).decode('utf-8')
        
        return base64_str
    
    def predict(self, image_path: str) -> dict:
        """
        Get prediction from the model
        
        Args:
            image_path: Path to input image
            
        Returns:
            Dictionary with predicted class and confidence
        """
        from app.core.preprocessing import ImagePreprocessor
        from app.constants import IDX_TO_CLASS
        import torch.nn.functional as F
        
        preprocessor = ImagePreprocessor()
        # Pass image_path directly, not PIL Image object
        image_tensor = preprocessor.preprocess(image_path).to(self.device)
        
        self.model.eval()
        with torch.no_grad():
            output = self.model(image_tensor)
            probs = F.softmax(output, dim=1)
            confidence, pred_idx = probs.max(dim=1)
            
        return {
            "predicted_class": IDX_TO_CLASS[pred_idx.item()],
            "confidence": float(confidence.item() * 100)
        }


class EnsembleGradCAM:
    """
    Grad-CAM for ensemble model
    Generates Grad-CAM for all 3 models
    """
    
    def __init__(self, models: dict, device: torch.device):
        """
        Initialize ensemble Grad-CAM
        
        Args:
            models: Dictionary of models {name: model}
            device: Device to run on
        """
        self.gradcams = {
            name: GradCAM(model, name, device)
            for name, model in models.items()
        }
        self.device = device
        
        logger.info(f"Ensemble Grad-CAM initialized with {len(self.gradcams)} models")
    
    def generate_all(
        self,
        image_path: str,
        alpha: float = 0.5
    ) -> dict:
        """
        Generate Grad-CAM for all models
        
        Args:
            image_path: Path to input image
            alpha: Overlay transparency
            
        Returns:
            Dictionary with Grad-CAM results for each model
        """
        results = {}
        
        for model_name, gradcam in self.gradcams.items():
            try:
                # Generate Grad-CAM image
                base64_image = gradcam.generate_base64(image_path, alpha=alpha)
                
                # Get prediction from this model
                prediction = gradcam.predict(image_path)
                
                results[model_name] = {
                    "success": True,
                    "gradcam_base64": base64_image,
                    "predicted_class": prediction["predicted_class"],
                    "confidence": prediction["confidence"]
                }
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                logger.error(f"Error generating Grad-CAM for {model_name}: {str(e)}\n{error_detail}")
                results[model_name] = {
                    "success": False,
                    "error": f"Không thể xử lý ảnh: {str(e)}"
                }
        
        return results


