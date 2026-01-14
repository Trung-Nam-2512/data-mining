"""
Mushroom Classification Model Architecture
"""
import torch
import torch.nn as nn
from torchvision import models
from torchvision.models import (
    ResNet50_Weights,
    EfficientNet_B0_Weights,
    MobileNet_V3_Large_Weights
)

from app.utils.logger import logger


class MushroomClassifier(nn.Module):
    """
    Mushroom Classification Model using Transfer Learning
    Supports 3 backbones: EfficientNet-B0, ResNet-50, MobileNetV3-Large
    """
    
    def __init__(
        self,
        backbone: str = "resnet50",
        num_classes: int = 11,
        pretrained: bool = False,
        freeze_backbone: bool = False
    ):
        """
        Initialize model
        
        Args:
            backbone: Backbone architecture name
            num_classes: Number of output classes
            pretrained: Use pretrained weights from ImageNet
            freeze_backbone: Freeze backbone weights (only train classifier)
        """
        super().__init__()
        self.backbone_name = backbone
        self.num_classes = num_classes
        
        # Initialize backbone
        if backbone == "resnet50":
            weights = ResNet50_Weights.DEFAULT if pretrained else None
            self.backbone = models.resnet50(weights=weights)
            num_features = self.backbone.fc.in_features
            self.backbone.fc = nn.Identity()
            
        elif backbone == "efficientnet_b0":
            weights = EfficientNet_B0_Weights.DEFAULT if pretrained else None
            self.backbone = models.efficientnet_b0(weights=weights)
            num_features = self.backbone.classifier[1].in_features
            self.backbone.classifier = nn.Identity()
            
        elif backbone == "mobilenet_v3_large":
            weights = MobileNet_V3_Large_Weights.DEFAULT if pretrained else None
            self.backbone = models.mobilenet_v3_large(weights=weights)
            num_features = self.backbone.classifier[0].in_features  # 960
            self.backbone.classifier = nn.Identity()
            
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
        
        # Freeze backbone if requested
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
        
        # Custom classifier head
        # Dropout(0.5) → Linear(features→512) → ReLU → Dropout(0.3) → Linear(512→num_classes)
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
        
        logger.info(
            f"Model initialized: {backbone}, "
            f"num_classes={num_classes}, "
            f"pretrained={pretrained}, "
            f"freeze_backbone={freeze_backbone}"
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: Input tensor (B, 3, H, W)
            
        Returns:
            Output logits (B, num_classes)
        """
        features = self.backbone(x)
        output = self.classifier(features)
        return output


