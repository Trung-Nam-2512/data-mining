"""
Evaluation Module for Mushroom Classification
"""
import torch
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from tqdm import tqdm

from src.model import create_model
from src.data_loader import MushroomDataLoader
from src.config import ALL_CLASSES, RESULTS_DIR, MODELS_DIR

class Evaluator:
    """
    Evaluation class for model performance assessment
    """
    
    def __init__(self, model, device, class_names=None):
        self.model = model.to(device)
        self.device = device
        self.class_names = class_names or ALL_CLASSES
        self.model.eval()
    
    def evaluate(self, data_loader):
        """
        Evaluate model on dataset
        
        Returns:
            Dictionary with evaluation metrics
        """
        all_preds = []
        all_labels = []
        all_probs = []
        
        with torch.no_grad():
            for images, labels in tqdm(data_loader, desc="Evaluating"):
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                probs = torch.softmax(outputs, dim=1)
                _, preds = torch.max(outputs, 1)
                
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                all_probs.extend(probs.cpu().numpy())
        
        all_preds = np.array(all_preds)
        all_labels = np.array(all_labels)
        all_probs = np.array(all_probs)
        
        # Calculate accuracy
        accuracy = np.mean(all_preds == all_labels)
        
        # Classification report
        report = classification_report(
            all_labels,
            all_preds,
            target_names=self.class_names,
            output_dict=True
        )
        
        # Confusion matrix
        cm = confusion_matrix(all_labels, all_preds)
        
        return {
            "accuracy": accuracy,
            "predictions": all_preds,
            "labels": all_labels,
            "probabilities": all_probs,
            "classification_report": report,
            "confusion_matrix": cm
        }
    
    def plot_confusion_matrix(self, cm, save_path=None):
        """Plot confusion matrix"""
        plt.figure(figsize=(12, 10))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=self.class_names,
            yticklabels=self.class_names,
            cbar_kws={'label': 'Count'}
        )
        plt.title('Confusion Matrix', fontsize=16, fontweight='bold')
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.savefig(RESULTS_DIR / "confusion_matrix.png", dpi=300, bbox_inches='tight')
        
        plt.close()
    
    def print_classification_report(self, report):
        """Print detailed classification report"""
        print("\n" + "="*70)
        print("CLASSIFICATION REPORT")
        print("="*70)
        
        print(f"\nOverall Accuracy: {report['accuracy']:.4f}")
        print(f"\nPer-Class Metrics:")
        print("-"*70)
        print(f"{'Class':<20} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<10}")
        print("-"*70)
        
        for class_name in self.class_names:
            if class_name in report:
                metrics = report[class_name]
                print(f"{class_name:<20} {metrics['precision']:<12.4f} {metrics['recall']:<12.4f} "
                      f"{metrics['f1-score']:<12.4f} {int(metrics['support']):<10}")
        
        print("-"*70)
        print(f"{'Macro Avg':<20} {report['macro avg']['precision']:<12.4f} "
              f"{report['macro avg']['recall']:<12.4f} {report['macro avg']['f1-score']:<12.4f} "
              f"{int(report['macro avg']['support']):<10}")
        print(f"{'Weighted Avg':<20} {report['weighted avg']['precision']:<12.4f} "
              f"{report['weighted avg']['recall']:<12.4f} {report['weighted avg']['f1-score']:<12.4f} "
              f"{int(report['weighted avg']['support']):<10}")
        print("="*70)

def load_model(model_path, device):
    """Load trained model"""
    checkpoint = torch.load(model_path, map_location=device)
    config = checkpoint.get('config', {})
    
    model = create_model(**config)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    return model, checkpoint

def main():
    """Main evaluation function"""
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Find best model
    model_files = list(MODELS_DIR.glob("best_model_*.pth"))
    if not model_files:
        print("No model found! Please train a model first.")
        return
    
    # Use most recent best model
    model_path = sorted(model_files)[-1]
    print(f"Loading model from: {model_path}")
    
    # Load model
    model, checkpoint = load_model(model_path, device)
    print(f"Model loaded from epoch {checkpoint['epoch']}")
    print(f"Validation accuracy: {checkpoint['val_acc']:.2f}%")
    
    # Create data loaders
    print("\nLoading data...")
    data_loader = MushroomDataLoader(use_transfer_data=True)
    _, _, test_loader = data_loader.create_data_loaders()
    
    # Evaluate
    print("\nEvaluating on test set...")
    evaluator = Evaluator(model, device)
    results = evaluator.evaluate(test_loader)
    
    # Print results
    print(f"\nTest Accuracy: {results['accuracy']*100:.2f}%")
    evaluator.print_classification_report(results['classification_report'])
    
    # Plot confusion matrix
    print("\nGenerating confusion matrix...")
    evaluator.plot_confusion_matrix(results['confusion_matrix'])
    print("Confusion matrix saved to results/confusion_matrix.png")
    
    print("\nEvaluation completed!")

if __name__ == "__main__":
    main()

