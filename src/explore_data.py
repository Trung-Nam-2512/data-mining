"""
Data Exploration Script
Visualize dataset statistics and sample images
"""
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pandas as pd

from src.data_loader import MushroomDataLoader
from src.config import RESULTS_DIR

def explore_dataset():
    """Explore and visualize dataset"""
    print("="*70)
    print("DATASET EXPLORATION")
    print("="*70)
    
    # Create data loader
    data_loader = MushroomDataLoader(use_transfer_data=True)
    
    # Get statistics
    print("\n1. Dataset Statistics:")
    stats = data_loader.get_data_statistics()
    print(stats)
    
    total_images = stats['count'].sum()
    print(f"\nTotal images: {total_images}")
    
    # Visualize class distribution
    print("\n2. Generating visualizations...")
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Bar plot
    ax1 = axes[0]
    stats_sorted = stats.sort_values('count', ascending=True)
    ax1.barh(stats_sorted.index, stats_sorted['count'], color='steelblue')
    ax1.set_xlabel('Number of Images', fontsize=12)
    ax1.set_ylabel('Mushroom Genus', fontsize=12)
    ax1.set_title('Class Distribution', fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # Pie chart
    ax2 = axes[1]
    colors = plt.cm.Set3(range(len(stats)))
    ax2.pie(stats['count'], labels=stats.index, autopct='%1.1f%%', 
            startangle=90, colors=colors)
    ax2.set_title('Class Distribution (Percentage)', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "dataset_distribution.png", dpi=300, bbox_inches='tight')
    print(f"✓ Saved visualization to {RESULTS_DIR / 'dataset_distribution.png'}")
    plt.close()
    
    # Source vs Target domain comparison
    source_classes = stats.index[:9]
    target_classes = stats.index[9:]
    
    source_count = stats.loc[source_classes, 'count'].sum()
    target_count = stats.loc[target_classes, 'count'].sum()
    
    print("\n3. Domain Comparison:")
    print(f"Source Domain (9 classes): {source_count} images")
    print(f"Target Domain (2 classes): {target_count} images")
    print(f"Ratio: {source_count/target_count:.2f}:1")
    
    # Toxicity distribution
    from src.toxicity import ToxicityClassifier
    toxicity_clf = ToxicityClassifier()
    
    poisonous_count = sum(stats.loc[genus, 'count'] for genus in toxicity_clf.get_all_poisonous() if genus in stats.index)
    edible_count = sum(stats.loc[genus, 'count'] for genus in toxicity_clf.get_all_edible() if genus in stats.index)
    
    print("\n4. Toxicity Distribution:")
    print(f"Poisonous (P): {poisonous_count} images")
    print(f"Edible (E): {edible_count} images")
    print(f"Ratio: {poisonous_count/edible_count:.2f}:1")
    
    # Visualize toxicity distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    toxicity_data = pd.DataFrame({
        'Category': ['Poisonous (P)', 'Edible (E)'],
        'Count': [poisonous_count, edible_count]
    })
    ax.bar(toxicity_data['Category'], toxicity_data['Count'], 
           color=['#f44336', '#4caf50'], alpha=0.7)
    ax.set_ylabel('Number of Images', fontsize=12)
    ax.set_title('Toxicity Distribution', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    for i, v in enumerate(toxicity_data['Count']):
        ax.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "toxicity_distribution.png", dpi=300, bbox_inches='tight')
    print(f"✓ Saved visualization to {RESULTS_DIR / 'toxicity_distribution.png'}")
    plt.close()
    
    print("\n" + "="*70)
    print("Exploration completed!")
    print("="*70)

if __name__ == "__main__":
    explore_dataset()

