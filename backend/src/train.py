"""
Training Pipeline for Mushroom Classification
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
from tqdm import tqdm
import os
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime

from src.model import create_model
from src.data_loader import MushroomDataLoader
from src.config import TRAIN_CONFIG, MODEL_CONFIG, MODELS_DIR, RESULTS_DIR

class Trainer:
    """
    Training class for Mushroom Classification
    """
    
    def __init__(self, model, device, save_dir=None):
        self.model = model.to(device)
        self.device = device
        self.save_dir = save_dir or MODELS_DIR
        
        # Loss and optimizer
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=TRAIN_CONFIG["learning_rate"],
            weight_decay=1e-4
        )
        self.scheduler = ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.5,
            patience=5,
            verbose=True
        )
        
        # Training history
        self.train_losses = []
        self.train_accs = []
        self.val_losses = []
        self.val_accs = []
        
    def train_epoch(self, train_loader):
        """Train for one epoch"""
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(train_loader, desc="Training")
        for images, labels in pbar:
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Statistics
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            # Update progress bar
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{100 * correct / total:.2f}%'
            })
        
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100 * correct / total
        
        return epoch_loss, epoch_acc
    
    def validate(self, val_loader):
        """Validate model"""
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in tqdm(val_loader, desc="Validating"):
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                
                running_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        epoch_loss = running_loss / len(val_loader)
        epoch_acc = 100 * correct / total
        
        return epoch_loss, epoch_acc
    
    def train(self, train_loader, val_loader, num_epochs=None):
        """Full training loop"""
        num_epochs = num_epochs or TRAIN_CONFIG["num_epochs"]
        best_val_acc = 0.0
        best_model_path = None
        
        print(f"Starting training for {num_epochs} epochs...")
        print(f"Device: {self.device}")
        print(f"Model: {MODEL_CONFIG['backbone']}")
        print(f"Number of classes: {MODEL_CONFIG['num_classes']}")
        print("-" * 50)
        
        for epoch in range(num_epochs):
            print(f"\nEpoch {epoch+1}/{num_epochs}")
            
            # Train
            train_loss, train_acc = self.train_epoch(train_loader)
            self.train_losses.append(train_loss)
            self.train_accs.append(train_acc)
            
            # Validate
            val_loss, val_acc = self.validate(val_loader)
            self.val_losses.append(val_loss)
            self.val_accs.append(val_acc)
            
            # Learning rate scheduling
            self.scheduler.step(val_loss)
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                best_model_path = self.save_dir / f"best_model_epoch_{epoch+1}.pth"
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'val_acc': val_acc,
                    'train_acc': train_acc,
                    'config': MODEL_CONFIG
                }, best_model_path)
                print(f"✓ Saved best model (Val Acc: {val_acc:.2f}%)")
            
            print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
            print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        # Save final model
        final_model_path = self.save_dir / "final_model.pth"
        torch.save({
            'epoch': num_epochs,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'train_losses': self.train_losses,
            'train_accs': self.train_accs,
            'val_losses': self.val_losses,
            'val_accs': self.val_accs,
            'config': MODEL_CONFIG
        }, final_model_path)
        
        print(f"\nTraining completed!")
        print(f"Best validation accuracy: {best_val_acc:.2f}%")
        print(f"Best model saved at: {best_model_path}")
        print(f"Final model saved at: {final_model_path}")
        
        return best_model_path
    
    def plot_training_history(self, save_path=None):
        """Plot training history"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Loss plot
        ax1.plot(self.train_losses, label='Train Loss')
        ax1.plot(self.val_losses, label='Val Loss')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.set_title('Training and Validation Loss')
        ax1.legend()
        ax1.grid(True)
        
        # Accuracy plot
        ax2.plot(self.train_accs, label='Train Acc')
        ax2.plot(self.val_accs, label='Val Acc')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy (%)')
        ax2.set_title('Training and Validation Accuracy')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Training history saved to {save_path}")
        else:
            plt.savefig(RESULTS_DIR / "training_history.png", dpi=300, bbox_inches='tight')
        
        plt.close()

def main():
    """Main training function"""
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Create data loaders
    print("Loading data...")
    data_loader = MushroomDataLoader(use_transfer_data=True)
    train_loader, val_loader, test_loader = data_loader.create_data_loaders()
    
    # Print data statistics
    stats = data_loader.get_data_statistics()
    print("\nDataset Statistics:")
    print(stats)
    print(f"\nTotal images: {stats['count'].sum()}")
    
    # Create model
    print("\nCreating model...")
    model = create_model()
    print(f"Model created: {MODEL_CONFIG['backbone']}")
    print(f"Total parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"Trainable parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
    
    # Create trainer
    trainer = Trainer(model, device)
    
    # Train
    best_model_path = trainer.train(train_loader, val_loader)
    
    # Plot training history
    trainer.plot_training_history()
    
    print("\nTraining completed successfully!")

if __name__ == "__main__":
    main()

