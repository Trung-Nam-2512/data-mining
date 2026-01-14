"""
Image preprocessing for mushroom classification
"""
import torch
from torchvision import transforms
from PIL import Image
from pathlib import Path
from typing import Union

from app.utils.logger import logger


class ImagePreprocessor:
    """Image preprocessing pipeline for inference"""
    
    def __init__(self, image_size: int = 224):
        """
        Initialize preprocessor
        
        Args:
            image_size: Target image size (default: 224)
        """
        self.image_size = image_size
        
        # Validation/Test transforms (no augmentation for inference)
        self.transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],  # ImageNet mean
                std=[0.229, 0.224, 0.225]     # ImageNet std
            )
        ])
        
        logger.info(f"Image preprocessor initialized (size: {image_size}x{image_size})")
    
    def preprocess(self, image_path: Union[str, Path]) -> torch.Tensor:
        """
        Preprocess image for inference
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image tensor (1, 3, H, W)
            
        Raises:
            ValueError: If image cannot be loaded or processed
        """
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Apply transforms
            image_tensor = self.transform(image)
            
            # Add batch dimension
            image_tensor = image_tensor.unsqueeze(0)
            
            logger.debug(f"Preprocessed image: {Path(image_path).name} -> {image_tensor.shape}")
            
            return image_tensor
            
        except Exception as e:
            error_msg = f"Không thể xử lý ảnh: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def preprocess_batch(self, image_paths: list) -> torch.Tensor:
        """
        Preprocess batch of images
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Batch of preprocessed images (B, 3, H, W)
        """
        batch_tensors = []
        
        for image_path in image_paths:
            tensor = self.preprocess(image_path)
            batch_tensors.append(tensor)
        
        # Stack into batch
        batch_tensor = torch.cat(batch_tensors, dim=0)
        
        logger.debug(f"Preprocessed batch: {len(image_paths)} images -> {batch_tensor.shape}")
        
        return batch_tensor


# Global preprocessor instance
preprocessor = ImagePreprocessor()


