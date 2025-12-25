"""
Toxicity Classification Module
Maps mushroom genus to toxicity level
"""
from typing import Dict, Tuple
from src.config import TOXICITY_MAPPING, ALL_CLASSES

class ToxicityClassifier:
    """
    Classifies mushroom toxicity based on genus name
    """
    
    def __init__(self):
        self.mapping = TOXICITY_MAPPING
        self.poisonous_classes = [cls for cls, tox in self.mapping.items() if tox == "P"]
        self.edible_classes = [cls for cls, tox in self.mapping.items() if tox == "E"]
    
    def classify(self, genus: str) -> Tuple[str, str]:
        """
        Classify toxicity based on genus name
        
        Args:
            genus: Name of the mushroom genus
            
        Returns:
            Tuple of (toxicity_label, toxicity_description)
        """
        if genus not in self.mapping:
            raise ValueError(f"Unknown genus: {genus}. Must be one of {ALL_CLASSES}")
        
        toxicity = self.mapping[genus]
        description = "Độc (Poisonous)" if toxicity == "P" else "Ăn được (Edible)"
        
        return toxicity, description
    
    def get_toxicity_info(self, genus: str) -> Dict:
        """
        Get detailed toxicity information
        
        Args:
            genus: Name of the mushroom genus
            
        Returns:
            Dictionary with toxicity information
        """
        toxicity, description = self.classify(genus)
        
        return {
            "genus": genus,
            "toxicity_label": toxicity,
            "toxicity_description": description,
            "is_poisonous": toxicity == "P",
            "is_edible": toxicity == "E",
            "warning": "⚠️ CẢNH BÁO: Nấm này có độc tính!" if toxicity == "P" else "✅ An toàn để ăn"
        }
    
    def get_all_poisonous(self) -> list:
        """Return list of all poisonous genera"""
        return self.poisonous_classes.copy()
    
    def get_all_edible(self) -> list:
        """Return list of all edible genera"""
        return self.edible_classes.copy()

