"""
Constants for Mushroom Classification System
"""

# Class names (11 genera - Phase 2)
ALL_CLASSES = [
    "Agaricus",
    "Amanita",
    "Boletus",
    "Cortinarius",
    "Entoloma",
    "Hygrocybe",
    "Lactarius",
    "Russula",
    "Suillus",
    "Exidia",
    "Inocybe"
]

# Toxicity mapping: P = Poisonous, E = Edible
TOXICITY_MAPPING = {
    # Poisonous (4 genera)
    "Amanita": "P",
    "Cortinarius": "P",
    "Entoloma": "P",
    "Inocybe": "P",
    # Edible (7 genera)
    "Agaricus": "E",
    "Boletus": "E",
    "Hygrocybe": "E",
    "Lactarius": "E",
    "Russula": "E",
    "Suillus": "E",
    "Exidia": "E"
}

# Class to index mapping
CLASS_TO_IDX = {cls: idx for idx, cls in enumerate(ALL_CLASSES)}
IDX_TO_CLASS = {idx: cls for cls, idx in CLASS_TO_IDX.items()}

# Model names
MODEL_NAMES = ["resnet50", "efficientnet_b0", "mobilenet_v3_large"]

# Vietnamese toxicity labels
TOXICITY_LABELS_VI = {
    "P": "Độc",
    "E": "Ăn được"
}

# Toxicity warnings in Vietnamese
TOXICITY_WARNINGS = {
    "P": "⚠️ CẢNH BÁO: Nấm này là NẤM ĐỘC! Không ăn!",
    "E": "✅ An toàn: Nấm này CÓ THỂ ĂN ĐƯỢC (vẫn cần xác nhận thêm bởi chuyên gia)"
}

# Color coding for UI
TOXICITY_COLORS = {
    "P": "#ff4444",  # Red
    "E": "#4CAF50"   # Green
}

# Model accuracy (for reference)
MODEL_ACCURACY = {
    "resnet50": 91.59,
    "efficientnet_b0": 88.33,
    "mobilenet_v3_large": 87.64
}


