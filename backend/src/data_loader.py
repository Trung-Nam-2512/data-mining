"""
Data Loading and Preprocessing Module
"""
import os
import torch
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms
from PIL import Image
import pandas as pd
from pathlib import Path
from typing import Tuple, List, Dict
from src.config import (
    SOURCE_DATA_DIR, TARGET_DATA_DIR, ALL_CLASSES, 
    TRAIN_CONFIG, MODEL_CONFIG
)

class MushroomDataset(Dataset):
    """
    Custom Dataset for Mushroom Images
    """
    
    def __init__(self, image_paths: List[str], labels: List[int], transform=None):
        """
        Args:
            image_paths: List of image file paths
            labels: List of class labels (integers)
            transform: Optional transform to be applied on a sample
        """
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]
        
        try:
            image = Image.open(img_path).convert('RGB')
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            # Return a black image as fallback
            image = Image.new('RGB', (224, 224), color='black')
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

class MushroomDataLoader:
    """
    Data Loader for Mushroom Classification
    Handles both Source and Target domain data
    """
    
    def __init__(self, use_transfer_data: bool = True):
        """
        Args:
            use_transfer_data: Whether to include transfer learning data
        """
        self.source_dir = Path(SOURCE_DATA_DIR)
        self.target_dir = Path(TARGET_DATA_DIR)
        self.use_transfer_data = use_transfer_data
        self.class_to_idx = {cls: idx for idx, cls in enumerate(ALL_CLASSES)}
        self.idx_to_class = {idx: cls for cls, idx in self.class_to_idx.items()}
        
    def load_data_paths(self) -> Tuple[List[str], List[int]]:
        """
        Load all image paths and their corresponding labels
        
        Returns:
            Tuple of (image_paths, labels)
        """
        image_paths = []
        labels = []
        
        # Load source domain data
        for genus in ALL_CLASSES[:9]:  # First 9 are source domain
            genus_dir = self.source_dir / genus
            if genus_dir.exists():
                for img_file in genus_dir.glob("*.jpg"):
                    image_paths.append(str(img_file))
                    labels.append(self.class_to_idx[genus])
        
        # Load target domain data if enabled
        if self.use_transfer_data:
            for genus in ALL_CLASSES[9:]:  # Last 2 are target domain
                genus_dir = self.target_dir / genus
                if genus_dir.exists():
                    for img_file in genus_dir.glob("*.jpg"):
                        image_paths.append(str(img_file))
                        labels.append(self.class_to_idx[genus])
        
        return image_paths, labels
    
    def get_data_statistics(self) -> pd.DataFrame:
        """
        Get statistics about the dataset
        
        Returns:
            DataFrame with class distribution
        """
        image_paths, labels = self.load_data_paths()
        
        stats = {}
        for idx, count in enumerate(torch.bincount(torch.tensor(labels))):
            genus = self.idx_to_class[idx]
            stats[genus] = {
                "count": count.item(),
                "class_idx": idx
            }
        
        df = pd.DataFrame.from_dict(stats, orient='index')
        df = df.sort_values('count', ascending=False)
        return df
    
    def create_data_loaders(
        self, 
        batch_size: int = None,
        train_split: float = None,
        val_split: float = None,
        test_split: float = None
    ) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """
        Create train, validation, and test data loaders
        
        Returns:
            Tuple of (train_loader, val_loader, test_loader)
        """
        batch_size = batch_size or TRAIN_CONFIG["batch_size"]
        train_split = train_split or TRAIN_CONFIG["train_split"]
        val_split = val_split or TRAIN_CONFIG["val_split"]
        test_split = test_split or TRAIN_CONFIG["test_split"]
        
        # Load data paths
        image_paths, labels = self.load_data_paths()
        
        # Data augmentation for training
        train_transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomCrop(224),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Validation/Test transforms (no augmentation)
        val_test_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Create dataset
        full_dataset = MushroomDataset(image_paths, labels, transform=train_transform)
        
        # Split dataset
        total_size = len(full_dataset)
        train_size = int(train_split * total_size)
        val_size = int(val_split * total_size)
        test_size = total_size - train_size - val_size
        
        train_dataset, val_dataset, test_dataset = random_split(
            full_dataset, 
            [train_size, val_size, test_size],
            generator=torch.Generator().manual_seed(TRAIN_CONFIG["random_seed"])
        )
        
        # Update transforms for val and test
        val_dataset.dataset.transform = val_test_transform
        test_dataset.dataset.transform = val_test_transform
        
        # Create data loaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=TRAIN_CONFIG["num_workers"],
            pin_memory=True
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=TRAIN_CONFIG["num_workers"],
            pin_memory=True
        )
        
        test_loader = DataLoader(
            test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=TRAIN_CONFIG["num_workers"],
            pin_memory=True
        )
        
        return train_loader, val_loader, test_loader

