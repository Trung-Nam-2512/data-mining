# 🍄 Hệ thống Nhận diện Chi Nấm và Cảnh báo Độc tính

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-orange.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2+-61dafb.svg)](https://react.dev/)

Hệ thống sử dụng **Deep Learning** và **Transfer Learning** để nhận diện 11 chi nấm từ ảnh và tự động cảnh báo độc tính. Dự án được xây dựng với kiến trúc hiện đại: **Backend FastAPI** và **Frontend React**, cùng với **Jupyter Notebook** để training và phân tích mô hình.

---

## 📋 Mục lục

- [Tổng quan](#-tổng-quan)
- [Tính năng](#-tính-năng)
- [Kiến trúc Hệ thống](#-kiến-trúc-hệ-thống)
- [Cài đặt](#-cài-đặt)
- [Hướng dẫn Sử dụng](#-hướng-dẫn-sử-dụng)
- [📓 Jupyter Notebook - Training Pipeline](#-jupyter-notebook---training-pipeline)
- [Kết quả](#-kết-quả)
- [API Documentation](#-api-documentation)
- [Công nghệ Sử dụng](#-công-nghệ-sử-dụng)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Lưu ý Quan trọng](#-lưu-ý-quan-trọng)
- [License](#-license)

---

## 🎯 Tổng quan

Dự án này được phát triển cho **bài tập lớn môn Khai phá dữ liệu (Data Mining)**, sử dụng các kỹ thuật Deep Learning tiên tiến để:

- **Nhận diện 11 chi nấm** từ ảnh (9 chi từ Source Domain + 2 chi từ Target Domain)
- **Tự động phân loại độc tính** (Poisonous/Edible) với ưu tiên an toàn cao
- **So sánh 3 backbone models** (ResNet-50, EfficientNet-B0, MobileNetV3-Large)
- **Ensemble Learning** với Soft Voting để tăng độ chính xác
- **Explainable AI** với Grad-CAM để giải thích kết quả

### Dataset

- **Tổng số ảnh**: 7,766 ảnh (đã lọc 1 ảnh corrupted)
- **Source Domain**: 6,713 ảnh (86.4%) - 9 chi nấm
- **Target Domain**: 1,053 ảnh (13.6%) - 2 chi nấm (Exidia, Inocybe)
- **Phân phối độc tính**:
  - **Poisonous**: 2,568 ảnh (33.1%) - 4 chi nấm
  - **Edible**: 5,198 ảnh (66.9%) - 7 chi nấm
- **Train/Val/Test Split**: 70/15/15 với stratified sampling

### Kết quả Đạt được

| Model | Test Accuracy | Val Accuracy | Training Time | Status |
|-------|---------------|--------------|---------------|--------|
| **ResNet-50** | **91.59%** | 93.39% | 7.60 min | ✅ Best |
| EfficientNet-B0 | 88.33% | 88.41% | 7.13 min | ✅ Good |
| MobileNetV3-Large | 87.64% | 87.73% | 6.09 min | ✅ Fastest |

---

## ✨ Tính năng

### Core Features

- ✅ **Nhận diện 11 chi nấm** với độ chính xác cao (>90%)
- ✅ **Tự động cảnh báo độc tính** với ưu tiên an toàn (recall cao cho nấm độc)
- ✅ **Ensemble Learning** kết hợp 3 models để tăng độ chính xác
- ✅ **Explainable AI** với Grad-CAM để giải thích vùng ảnh quan trọng
- ✅ **Batch Prediction** xử lý nhiều ảnh cùng lúc
- ✅ **RESTful API** dễ tích hợp
- ✅ **Web Interface** hiện đại và responsive

### Advanced Features

- 🔬 **Cost-Sensitive Learning**: Class weights 4x cho nấm độc
- 🎯 **Label Smoothing**: 10% để chống overfitting
- ⚡ **Mixed Precision Training**: FP16 để tăng tốc 2x
- 🎨 **Data Augmentation**: 9 loại augmentation nâng cao
- 📊 **Comprehensive Evaluation**: Confusion matrix, classification report, per-class metrics

---

## 🏗️ Kiến trúc Hệ thống

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Upload     │  │  Prediction  │  │   Grad-CAM   │     │
│  │   Image      │  │   Results    │  │  Heatmaps    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────────┬───────────────────────────────────┘
                         │ HTTP/REST
┌───────────────────────▼───────────────────────────────────┐
│              Backend (FastAPI)                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         Ensemble Inference Engine                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │  │
│  │  │ ResNet-50│  │Efficient │  │ MobileNet│        │  │
│  │  │          │  │   -B0    │  │   V3-L   │        │  │
│  │  └──────────┘  └──────────┘  └──────────┘        │  │
│  │              Soft Voting Ensemble                  │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         Grad-CAM Visualization                      │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────┐
│         Jupyter Notebook (Training & Analysis)            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Data Preprocessing → Model Training → Evaluation   │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐   │  │
│  │  │   Data     │  │  Training  │  │ Evaluation │   │  │
│  │  │  Loading   │  │  Pipeline  │  │  Metrics   │   │  │
│  │  └────────────┘  └────────────┘  └────────────┘   │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Cấu trúc Thư mục

```
DataMining/
├── 📓 mushroom_classification.ipynb    # Jupyter Notebook chính (TRAINING)
│
├── backend/                            # FastAPI Backend
│   ├── app/
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── api/v1/                    # API version 1 routes
│   │   │   ├── endpoints/
│   │   │   │   ├── predictions.py    # Prediction endpoints
│   │   │   │   ├── gradcam.py        # Grad-CAM endpoints
│   │   │   │   └── model.py          # Model info endpoints
│   │   ├── core/                      # Core functionality
│   │   │   ├── model_loader.py       # Model loading
│   │   │   ├── ensemble.py            # Ensemble inference
│   │   │   ├── gradcam.py            # Grad-CAM implementation
│   │   │   └── preprocessing.py      # Image preprocessing
│   │   ├── services/                  # Business logic
│   │   └── utils/                     # Utilities
│   ├── src/                           # Legacy ML code
│   ├── requirements.txt               # Python dependencies
│   └── run.py                         # Run script
│
├── frontend/                          # React Frontend
│   ├── src/
│   │   ├── components/               # Reusable components
│   │   ├── pages/                    # Page components
│   │   ├── services/                 # API services
│   │   └── hooks/                    # Custom React hooks
│   └── package.json                  # Node dependencies
│
├── models/                            # Trained models
│   ├── best_model_resnet50_improved.pth
│   ├── best_model_efficientnet_b0_improved.pth
│   └── best_model_mobilenet_v3_large_improved.pth
│
├── archive/                           # Source domain data
│   └── Mushrooms/                     # 9 classes
│
├── Transferdata/                      # Target domain data
│   └── Transferdata/                  # 2 classes
│
├── results/                           # Training results
│   ├── plots/                        # Training curves
│   ├── reports/                      # Classification reports
│   └── logs/                         # Training logs
│
└── README.md                          # This file
```

---

## 🚀 Cài đặt

### Yêu cầu Hệ thống

- **Python**: 3.8 trở lên
- **Node.js**: 16+
- **PyTorch**: 2.0+ (với CUDA support nếu có GPU)
- **GPU**: Khuyến nghị (NVIDIA GPU với CUDA) để training nhanh hơn

### 1. Clone Repository

```bash
git clone <repository-url>
cd DataMining
```

### 2. Backend Setup

```bash
# Di chuyển vào thư mục backend
cd backend

# Tạo virtual environment (khuyến nghị)
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Di chuyển vào thư mục frontend
cd frontend

# Cài đặt dependencies
npm install
```

### 4. Download Models

Đảm bảo các model đã được train và lưu trong thư mục `models/`:

- `best_model_resnet50_improved.pth`
- `best_model_efficientnet_b0_improved.pth`
- `best_model_mobilenet_v3_large_improved.pth`

> **Lưu ý**: Nếu chưa có models, xem phần [Jupyter Notebook - Training Pipeline](#-jupyter-notebook---training-pipeline) để train models.

---

## 📖 Hướng dẫn Sử dụng

### Chạy Backend

```bash
cd backend
python run.py
```

Hoặc sử dụng uvicorn trực tiếp:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend sẽ chạy tại: `http://localhost:8000`

API Documentation (Swagger UI): `http://localhost:8000/docs`

### Chạy Frontend

```bash
cd frontend
npm run dev
```

Frontend sẽ chạy tại: `http://localhost:3000`

### Sử dụng Web Interface

1. Mở trình duyệt và truy cập `http://localhost:3000`
2. Upload ảnh nấm (JPG, JPEG, PNG)
3. Xem kết quả nhận diện và cảnh báo độc tính
4. Xem Grad-CAM heatmaps để hiểu vùng ảnh quan trọng

---

## 📓 Jupyter Notebook - Training Pipeline

> **Phần này là trọng tâm của dự án** - Chi tiết về quá trình training và phân tích mô hình.

### Tổng quan Notebook

File `mushroom_classification.ipynb` chứa toàn bộ quá trình:

- **Data Preprocessing**: Load, filter, explore, augment
- **Model Training**: Fine-tuning 3 backbone models
- **Evaluation**: Comprehensive metrics và visualization
- **Analysis**: So sánh models, error analysis, Grad-CAM

### Cấu trúc Notebook

#### **1. Setup & Configuration** (Cell 1-4)

- **Import Libraries**: PyTorch, torchvision, sklearn, matplotlib, seaborn
- **Hardware Detection**: Tự động detect GPU/CPU và tối ưu batch size, num_workers
- **Configuration**:
  - Đường dẫn dữ liệu (Source Domain, Target Domain)
  - Danh sách 11 classes và toxicity mapping
  - Hyperparameters (batch size, learning rate, epochs, image size)

**Key Configurations:**

```python
TRAIN_CONFIG = {
    "batch_size": 192,              # Tự động tối ưu theo GPU
    "num_epochs": 50,
    "learning_rate": 0.001,
    "label_smoothing": 0.1,          # 10% label smoothing
    "use_differential_lr": True,     # Differential learning rates
    "backbone_lr_multiplier": 0.1,   # Backbone học chậm
    "classifier_lr_multiplier": 1.0, # Classifier học nhanh
    "use_mixed_precision": True      # FP16 training
}

MODEL_CONFIG = {
    "backbone": "resnet50",          # Hoặc "efficientnet_b0", "mobilenet_v3_large"
    "num_classes": 11,
    "pretrained": True,              # Transfer learning từ ImageNet
    "freeze_backbone": False         # Fine-tuning (không freeze)
}
```

#### **2. Data Loading & Exploration** (Cell 5-7)

- **Load Data Paths**:
  - Source Domain: 9 classes từ `archive/Mushrooms/`
  - Target Domain: 2 classes từ `Transferdata/Transferdata/`
- **Filter Corrupted Images**: Loại bỏ ảnh hỏng/truncated
- **Dataset Statistics**:
  - Phân phối classes
  - Phân phối độc tính (Poisonous/Edible)
  - So sánh Source vs Target Domain
- **Visualization**: Bar charts, pie charts, domain comparison

**Kết quả:**

```
Tổng số ảnh: 7,766 ảnh
- Source Domain: 6,713 ảnh (86.4%)
- Target Domain: 1,053 ảnh (13.6%)
- Poisonous: 2,568 ảnh (33.1%)
- Edible: 5,198 ảnh (66.9%)
```

#### **3. Data Preprocessing** (Cell 8-13)

- **Custom Dataset Class**: `MushroomDataset` hỗ trợ torchvision transforms
- **Data Augmentation** (Training):

  ```python
  train_transform = transforms.Compose([
      transforms.Resize((256, 256)),
      transforms.RandomCrop(224),
      transforms.RandomHorizontalFlip(p=0.5),
      transforms.RandomVerticalFlip(p=0.3),
      transforms.RandomRotation(15),
      transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
      transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
      transforms.RandomApply([transforms.GaussianBlur(kernel_size=3)], p=0.2),
      transforms.ToTensor(),
      transforms.RandomErasing(p=0.1),
      transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
  ])
  ```

- **Validation/Test Transforms**: Chỉ resize và normalize (không augmentation)
- **Dataset Split**: 70/15/15 với stratified sampling
- **DataLoaders**: Tối ưu với persistent workers, prefetch factor, pin memory

**Kết quả:**

```
Train: 5,436 ảnh (70.0%)
Validation: 1,165 ảnh (15.0%)
Test: 1,165 ảnh (15.0%)
```

#### **4. Model Architecture** (Cell 14-16)

- **MushroomClassifier Class**:
  - Hỗ trợ 3 backbones: ResNet-50, EfficientNet-B0, MobileNetV3-Large
  - Transfer Learning với pre-trained weights từ ImageNet
  - Custom classifier head:

    ```
    Dropout(0.5) → Linear(features→512) → ReLU → Dropout(0.3) → Linear(512→11)
    ```

- **Forward Test**: Verify architecture hoạt động đúng

#### **5. Training Functions** (Cell 17-25)

- **train_epoch()**: Training một epoch với mixed precision support
- **validate()**: Validation với mixed precision support
- **train_single_backbone()**: Hàm helper để train từng backbone
  - Setup logger
  - Training loop với early stopping
  - Save best model
  - Export training summary
  - Save training curves, confusion matrix, classification report

**Training Process:**

```python
# 1. Load data và tạo DataLoaders
# 2. Tạo model với pre-trained weights
# 3. Setup optimizer với differential learning rates
# 4. Setup loss function với class weights + label smoothing
# 5. Training loop:
#    - Train epoch với mixed precision
#    - Validate
#    - Learning rate scheduling
#    - Early stopping check
#    - Save best model
# 6. Evaluate trên test set
# 7. Export results (plots, reports, logs)
```

#### **6. Training Execution** (Cell 26-28)

Train từng backbone riêng biệt để tránh memory leak:

- **Cell 26**: Train EfficientNet-B0
- **Cell 27**: Train ResNet-50
- **Cell 28**: Train MobileNetV3-Large

**Output cho mỗi model:**

- Best model checkpoint: `best_model_{backbone}_improved.pth`
- Training curves: `training_curves_{backbone}_{timestamp}.png`
- Confusion matrix: `confusion_matrix_{backbone}_{timestamp}.png`
- Classification report: `classification_report_{backbone}_{timestamp}.json`
- Training summary: `training_summary_{backbone}_{timestamp}.json`
- Training log: `training_{backbone}_{timestamp}.log`

#### **7. Results Analysis** (Cell 29-35)

- **Load Results Summary**: Tổng hợp kết quả từ tất cả models
- **Comparison Charts**:
  - Accuracy comparison
  - Training time comparison
  - Efficiency comparison
  - Per-class metrics comparison
- **Comprehensive Evaluation**:
  - Overall performance
  - Per-class analysis
  - Toxicity safety accuracy
  - Error analysis

#### **8. Grad-CAM Visualization** (Cell 36-40)

- **Grad-CAM Implementation**: Giải thích vùng ảnh quan trọng
- **Comparative Analysis**: So sánh Grad-CAM của 3 models
- **Error Analysis**: Phân tích các trường hợp nhầm lẫn

### Kỹ thuật Nâng cao Đã Triển khai

#### **1. Transfer Learning & Fine-tuning**

- **Pre-trained Models**: ResNet-50, EfficientNet-B0, MobileNetV3-Large từ ImageNet
- **Fine-tuning Strategy**:
  - Không freeze backbone (`freeze_backbone=False`)
  - Differential Learning Rates:
    - Backbone LR = 0.0001 (học chậm để giữ features tốt)
    - Classifier LR = 0.001 (học nhanh để bắt kịp)

#### **2. Cost-Sensitive Learning**

- **Class Weights**: Inverse frequency với multiplier 4x cho nấm độc

  ```python
  # Ví dụ: Amanita (525 mẫu, độc)
  weight = (total_samples / (num_classes * class_count)) * 4.0
  # → Weight cao → Phạt nặng khi đoán sai nấm độc
  ```

- **Mục tiêu**: Tăng recall cho nấm độc (giảm False Negatives - nguy hiểm!)

#### **3. Regularization Techniques**

- **Label Smoothing**: 10% để chống overfitting
- **Dropout**: 0.5 và 0.3 trong classifier head
- **Data Augmentation**: 9 loại augmentation để tăng đa dạng dữ liệu
- **Early Stopping**: Patience=5 epochs

#### **4. Training Optimization**

- **Mixed Precision Training (FP16)**: Tăng tốc ~2x, giảm memory ~50%
- **Model Compilation**: `torch.compile()` để tăng tốc inference
- **Learning Rate Scheduling**: `ReduceLROnPlateau` (factor=0.5, patience=5)
- **Hardware Optimization**:
  - Tự động detect GPU và tối ưu batch size, num_workers
  - Persistent workers, prefetch factor, pin memory

### Chạy Notebook

1. **Mở Jupyter Notebook**:

   ```bash
   jupyter notebook mushroom_classification.ipynb
   ```

2. **Chạy từng cell theo thứ tự**:
   - Cell 1-4: Setup và Configuration
   - Cell 5-7: Data Loading & Exploration
   - Cell 8-13: Data Preprocessing
   - Cell 14-16: Model Architecture
   - Cell 17-25: Training Functions
   - Cell 26-28: Training Execution (chọn backbone muốn train)
   - Cell 29-35: Results Analysis
   - Cell 36-40: Grad-CAM Visualization

3. **Lưu ý**:
   - Cần GPU để training nhanh (có thể dùng CPU nhưng chậm hơn nhiều)
   - Mỗi model training mất ~6-8 phút trên GPU A6000
   - Đảm bảo có đủ RAM và disk space

---

## 📊 Kết quả

### Best Model: ResNet-50

- **Test Accuracy**: **91.59%**
- **Validation Accuracy**: **93.39%**
- **Macro Avg F1-Score**: 90.57%
- **Weighted Avg F1-Score**: 91.59%
- **Training Time**: 7.60 phút (39 epochs)
- **Best Epoch**: 34

### So sánh 3 Models

| Model | Test Acc | Val Acc | Training Time | Best Epoch | Status |
|-------|----------|---------|---------------|------------|--------|
| **ResNet-50** | **91.59%** | 93.39% | 7.60 min | 34 | ✅ Best |
| EfficientNet-B0 | 88.33% | 88.41% | 7.13 min | 30 | ✅ Good |
| MobileNetV3-Large | 87.64% | 87.73% | 6.09 min | 28 | ✅ Fastest |

### Per-Class Performance (ResNet-50)

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| Agaricus | 0.94 | 0.95 | 0.94 | 53 |
| Amanita | 0.92 | 0.89 | 0.90 | 79 |
| Boletus | 0.95 | 0.96 | 0.95 | 161 |
| Cortinarius | 0.88 | 0.90 | 0.89 | 125 |
| Entoloma | 0.85 | 0.88 | 0.86 | 55 |
| Hygrocybe | 0.90 | 0.88 | 0.89 | 47 |
| Lactarius | 0.94 | 0.93 | 0.94 | 234 |
| Russula | 0.92 | 0.91 | 0.92 | 172 |
| Suillus | 0.93 | 0.92 | 0.92 | 47 |
| Exidia | 0.90 | 0.88 | 0.89 | 65 |
| Inocybe | 0.88 | 0.85 | 0.86 | 93 |

### Toxicity Safety Accuracy

- **Poisonous Recall**: 89.5% (rất quan trọng - giảm False Negatives)
- **Edible Precision**: 94.2%
- **Overall Safety**: Model ưu tiên an toàn với recall cao cho nấm độc

---

## 📡 API Documentation

### Base URL

```
http://localhost:8000
```

### Endpoints

#### **1. Health Check**

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-13T14:30:00"
}
```

#### **2. Model Information**

```http
GET /api/v1/model/info
```

**Response:**

```json
{
  "ensemble_type": "Soft Voting",
  "num_models": 3,
  "models": [
    {
      "name": "ResNet50",
      "accuracy": 91.59,
      "status": "loaded"
    },
    {
      "name": "EfficientNet-B0",
      "accuracy": 88.33,
      "status": "loaded"
    },
    {
      "name": "MobileNetV3-Large",
      "accuracy": 87.64,
      "status": "loaded"
    }
  ],
  "num_classes": 11,
  "device": "cuda"
}
```

#### **3. Get Classes**

```http
GET /api/v1/classes
```

**Response:**

```json
{
  "classes": [
    {
      "name": "Amanita",
      "toxicity": "P",
      "is_poisonous": true
    },
    ...
  ]
}
```

#### **4. Predict (Single Image)**

```http
POST /api/v1/predict
Content-Type: multipart/form-data
```

**Parameters:**

- `file`: Image file (JPG, JPEG, PNG)
- `top_k`: Number of top predictions (default: 3, max: 10)

**Response:**

```json
{
  "success": true,
  "image_filename": "mushroom.jpg",
  "ensemble_prediction": {
    "genus": "Amanita",
    "confidence": 95.23,
    "toxicity": {
      "is_poisonous": true,
      "label": "Poisonous",
      "warning": "CẢNH BÁO: Chi nấm này có độc tính!"
    }
  },
  "top_predictions": [
    {
      "rank": 1,
      "genus": "Amanita",
      "confidence": 95.23
    },
    ...
  ],
  "individual_models": [
    {
      "model": "ResNet50",
      "genus": "Amanita",
      "confidence": 96.5
    },
    ...
  ]
}
```

#### **5. Predict Batch**

```http
POST /api/v1/predict/batch
Content-Type: multipart/form-data
```

**Parameters:**

- `files`: List of image files (max 10)
- `top_k`: Number of top predictions per image

**Response:**

```json
{
  "success": true,
  "results": [
    {
      "image_filename": "mushroom1.jpg",
      "ensemble_prediction": {...},
      ...
    },
    ...
  ]
}
```

#### **6. Grad-CAM Visualization**

```http
POST /api/v1/gradcam
Content-Type: multipart/form-data
```

**Parameters:**

- `file`: Image file
- `model`: Model name (optional, default: all models)

**Response:**

```json
{
  "success": true,
  "image_filename": "mushroom.jpg",
  "gradcam_results": [
    {
      "model": "ResNet50",
      "heatmap_base64": "...",
      "overlay_base64": "..."
    },
    ...
  ]
}
```

Xem chi tiết API documentation tại: `http://localhost:8000/docs`

---

## 🛠️ Công nghệ Sử dụng

### Backend

- **FastAPI**: Modern, fast web framework
- **PyTorch**: Deep learning framework
- **Torchvision**: Pre-trained models và transforms
- **Pillow**: Image processing
- **NumPy, Pandas**: Data manipulation
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

### Frontend

- **React**: UI library
- **Vite**: Build tool
- **Axios**: HTTP client
- **Tailwind CSS**: Styling
- **Framer Motion**: Animations
- **Recharts**: Data visualization

### Machine Learning

- **PyTorch 2.0+**: Deep learning
- **Transfer Learning**: ImageNet pre-trained models
- **Ensemble Learning**: Soft Voting
- **Explainable AI**: Grad-CAM
- **Data Augmentation**: Torchvision transforms

---

## 🚢 Deployment

### Docker Deployment

#### **1. Build và Run với Docker Compose**

```bash
# Build và start tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### **2. Production Deployment**

```bash
# Sử dụng production config
docker-compose -f docker-compose.production.yml up -d
```

### Manual Deployment

#### **Backend**

```bash
cd backend
python run.py
```

#### **Frontend**

```bash
cd frontend
npm run build
npm run preview
```

---

## 🔧 Troubleshooting

### Backend không khởi động

- ✅ Kiểm tra Python version: `python --version` (cần 3.8+)
- ✅ Kiểm tra dependencies: `pip list`
- ✅ Kiểm tra models có trong `models/` không
- ✅ Kiểm tra CUDA (nếu dùng GPU): `python -c "import torch; print(torch.cuda.is_available())"`

### Frontend không kết nối được Backend

- ✅ Kiểm tra Backend đang chạy tại `http://localhost:8000`
- ✅ Kiểm tra CORS configuration trong `backend/app/main.py`
- ✅ Kiểm tra `VITE_API_BASE_URL` trong `.env`

### Model không load được

- ✅ Kiểm tra file model có trong `models/` không
- ✅ Kiểm tra model path trong `backend/app/core/config.py`
- ✅ Xem log trong terminal để biết lỗi cụ thể

### Training chậm hoặc lỗi

- ✅ Kiểm tra GPU có được sử dụng không: `torch.cuda.is_available()`
- ✅ Giảm batch size nếu thiếu memory
- ✅ Kiểm tra disk space đủ không
- ✅ Kiểm tra data paths đúng không

---

## ⚠️ Lưu ý Quan trọng

**Hệ thống này chỉ mang tính chất tham khảo và phục vụ mục đích học tập.**

- ❌ **KHÔNG** nên dựa hoàn toàn vào kết quả để quyết định ăn nấm hoang dã
- ✅ **LUÔN** tham khảo ý kiến chuyên gia trước khi sử dụng nấm hoang dã
- ⚠️ Một số loại nấm có thể **gây tử vong** nếu ăn nhầm
- 📊 Model có thể có độ chính xác không hoàn hảo, đặc biệt với ảnh chất lượng kém

---

## 📄 License

Dự án này được tạo cho mục đích học tập (Data Mining Project).

---

## 📚 Tài liệu Tham khảo

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [Transfer Learning Guide](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)
- [Grad-CAM Paper](https://arxiv.org/abs/1610.02391)

---

## 👥 Contributors

Data Mining Project Team

---

## 📝 Changelog

### Version 1.0.0 (2024-01-13)

- ✅ Initial release
- ✅ 3 backbone models (ResNet-50, EfficientNet-B0, MobileNetV3-Large)
- ✅ Ensemble Soft Voting
- ✅ Grad-CAM visualization
- ✅ Web interface với React
- ✅ RESTful API với FastAPI
- ✅ Comprehensive evaluation và analysis

---

**Happy Coding! 🍄✨**
