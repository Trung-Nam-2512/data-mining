"""
Toxicity classification utilities
"""
from typing import Dict
from app.constants import (
    TOXICITY_MAPPING,
    TOXICITY_LABELS_VI,
    TOXICITY_WARNINGS,
    TOXICITY_COLORS
)


class ToxicityClassifier:
    """Utility class for toxicity classification"""
    
    @staticmethod
    def get_toxicity(genus: str) -> str:
        """
        Get toxicity label for a genus
        
        Args:
            genus: Mushroom genus name
            
        Returns:
            "P" for poisonous, "E" for edible
        """
        return TOXICITY_MAPPING.get(genus, "Unknown")
    
    @staticmethod
    def get_toxicity_info(genus: str) -> Dict[str, any]:
        """
        Get detailed toxicity information
        
        Args:
            genus: Mushroom genus name
            
        Returns:
            Dictionary with toxicity information
        """
        toxicity = ToxicityClassifier.get_toxicity(genus)
        
        return {
            "code": toxicity,
            "label": TOXICITY_LABELS_VI.get(toxicity, "Không xác định"),
            "is_poisonous": toxicity == "P",
            "warning": TOXICITY_WARNINGS.get(toxicity, "⚠️ Không xác định được độc tính"),
            "color": TOXICITY_COLORS.get(toxicity, "#999999")
        }
    
    @staticmethod
    def is_poisonous(genus: str) -> bool:
        """
        Check if genus is poisonous
        
        Args:
            genus: Mushroom genus name
            
        Returns:
            True if poisonous, False otherwise
        """
        return TOXICITY_MAPPING.get(genus) == "P"


# Global instance
toxicity_classifier = ToxicityClassifier()


