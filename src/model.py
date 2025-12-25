"""
Model Architecture Module
Uses Transfer Learning with pre-trained models
"""
import torch
import torch.nn as nn
import torchvision.models as models
from typing import Optional
from src.config import MODEL_CONFIG, ALL_CLASSES

class MushroomClassifier(nn.Module):
    """
    Mushroom Classification Model using Transfer Learning
    """
    
    def __init__(
        self,
        backbone: str = "resnet50",
        num_classes: int = None,
        pretrained: bool = True,
        freeze_backbone: bool = False
    ):
        """
        Args:
            backbone: Model backbone (resnet50, efficientnet_b0, mobilenet_v3)
            num_classes: Number of output classes
            pretrained: Whether to use pretrained weights
            freeze_backbone: Whether to freeze backbone for fine-tuning
        """
        super(MushroomClassifier, self).__init__()
        
        num_classes = num_classes or len(ALL_CLASSES)
        self.backbone_name = backbone
        self.num_classes = num_classes
        
        # Load backbone
        if backbone == "resnet50":
            self.backbone = models.resnet50(pretrained=pretrained)
            num_features = self.backbone.fc.in_features
            self.backbone.fc = nn.Identity()  # Remove final layer
            
        elif backbone == "efficientnet_b0":
            self.backbone = models.efficientnet_b0(pretrained=pretrained)
            num_features = self.backbone.classifier[1].in_features
            self.backbone.classifier = nn.Identity()
            
        elif backbone == "mobilenet_v3" or backbone == "mobilenet_v3_large":
            # Hỗ trợ cả mobilenet_v3 và mobilenet_v3_large
            from torchvision.models import MobileNet_V3_Large_Weights
            if pretrained:
                self.backbone = models.mobilenet_v3_large(weights=MobileNet_V3_Large_Weights.DEFAULT)
            else:
                self.backbone = models.mobilenet_v3_large(weights=None)
            num_features = self.backbone.classifier[0].in_features
            self.backbone.classifier = nn.Identity()
            
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
        
        # Freeze backbone if needed
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
        
        # Custom classifier head
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        """
        Forward pass
        """
        features = self.backbone(x)
        output = self.classifier(features)
        return output
    
    def get_feature_extractor(self):
        """
        Get feature extractor (backbone only)
        """
        return self.backbone

def create_model(
    backbone: Optional[str] = None,
    num_classes: Optional[int] = None,
    pretrained: Optional[bool] = None,
    freeze_backbone: Optional[bool] = None
) -> MushroomClassifier:
    """
    Factory function to create model
    
    Args:
        backbone: Model backbone
        num_classes: Number of classes
        pretrained: Use pretrained weights
        freeze_backbone: Freeze backbone
        
    Returns:
        MushroomClassifier model
    """
    config = MODEL_CONFIG.copy()
    
    if backbone is not None:
        config["backbone"] = backbone
    if num_classes is not None:
        config["num_classes"] = num_classes
    if pretrained is not None:
        config["pretrained"] = pretrained
    if freeze_backbone is not None:
        config["freeze_backbone"] = freeze_backbone
    
    model = MushroomClassifier(**config)
    return model

