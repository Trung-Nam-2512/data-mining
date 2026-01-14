# Hệ thống Nhận diện Chi Nấm và Cảnh báo Độc tính

Hệ thống sử dụng Deep Learning và Transfer Learning để nhận diện chi nấm từ ảnh và tự động cảnh báo độc tính. Dự án được xây dựng với kiến trúc hiện đại: Backend FastAPI và Frontend React.

## Tổng quan

Hệ thống này được phát triển cho bài tập lớn môn Khai phá dữ liệu (Data Mining), sử dụng:
- **Deep Learning**: MobileNet_V3_Large với Transfer Learning từ ImageNet
- **Backend**: FastAPI với RESTful API
- **Frontend**: React với Vite
- **Model Training**: PyTorch với Cost-Sensitive Learning

### Tính năng chính

- Nhận diện 9 chi nấm từ Source Domain (Phase 1)
- Tự động phân loại độc tính (Poisonous/Edible)
- API RESTful cho tích hợp
- Giao diện web hiện đại và responsive
- Batch prediction cho nhiều ảnh cùng lúc

## Kiến trúc Hệ thống

### Backend (FastAPI)

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/v1/              # API version 1 routes
│   │   ├── api.py          # Router aggregation
│   │   └── endpoints/      # Individual endpoints
│   ├── core/               # Configuration
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   └── utils/              # Utility functions
└── src/                    # Legacy ML code
```

### Frontend (React)

```
frontend/
├── src/
│   ├── components/         # Reusable components
│   ├── pages/              # Page components
│   ├── services/           # API services
│   ├── hooks/              # Custom React hooks
│   ├── utils/              # Utility functions
│   └── styles/             # CSS files
└── public/                 # Static assets
```

## Yêu cầu Hệ thống

### Backend
- Python 3.8 trở lên
- PyTorch 2.0+
- FastAPI
- Model đã được train (trong thư mục `models/`)

### Frontend
- Node.js 16+ 
- npm hoặc yarn

## Cài đặt

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

## Chạy Ứng dụng

### Backend

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

### Frontend

```bash
cd frontend
npm run dev
```

Frontend sẽ chạy tại: `http://localhost:3000`

## Cấu hình

### Backend Configuration

Các đường dẫn được cấu hình trong `backend/app/core/config.py`:

- `SOURCE_DATA_DIR`: Đường dẫn đến Source Domain data
- `TARGET_DATA_DIR`: Đường dẫn đến Target Domain data  
- `MODELS_DIR`: Đường dẫn đến thư mục models

### Frontend Configuration

API URL được cấu hình trong `frontend/src/services/api.js`:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
```

Có thể tạo file `.env` trong thư mục `frontend/`:

```
VITE_API_BASE_URL=http://localhost:8000
```

## API Endpoints

### Health Check
```
GET /health
```

### Model Information
```
GET /api/v1/model/info
```

Trả về thông tin về model đã load (backbone, số classes, device, phase).

### Get Classes
```
GET /api/v1/classes
```

Trả về danh sách tất cả classes với thông tin độc tính.

### Predict (Single Image)
```
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
  "best_prediction": {
    "genus": "Amanita",
    "confidence": 95.23,
    "toxicity": {
      "is_poisonous": true,
      "warning": "CẢNH BÁO: Chi nấm này có độc tính!",
      "toxicity_description": "Chi nấm này thuộc nhóm độc (Poisonous)"
    }
  },
  "top_predictions": [...],
  "all_probabilities": {...}
}
```

### Predict Batch
```
POST /api/v1/predict/batch
Content-Type: multipart/form-data
```

**Parameters:**
- `files`: List of image files (max 10)
- `top_k`: Number of top predictions per image

Xem chi tiết API documentation tại: `http://localhost:8000/docs`

## Dataset

### Source Domain (9 classes)
- Agaricus
- Amanita (Poisonous)
- Boletus
- Cortinarius (Poisonous)
- Entoloma (Poisonous)
- Hygrocybe
- Lactarius
- Russula
- Suillus

### Target Domain (2 classes - Phase 2)
- Exidia
- Inocybe (Poisonous)

### Toxicity Classification

**Poisonous (P):**
- Amanita
- Cortinarius
- Entoloma
- Inocybe

**Edible (E):**
- Tất cả các chi còn lại

## Model Training

Model được train trong Jupyter Notebook (`mushroom_classification.ipynb`):

- **Phase 1**: 9 classes từ Source Domain
- **Backbone**: MobileNet_V3_Large
- **Pre-trained**: ImageNet weights
- **Optimization**: CPU với tất cả cores
- **Cost-Sensitive Learning**: Class weights nhân đôi cho nấm độc

Model tốt nhất được lưu trong thư mục `models/` với format: `best_model_epoch_X.pth`

## Cấu trúc Dự án

```
DataMining/
├── backend/                 # FastAPI Backend
│   ├── app/                # Application code
│   │   ├── main.py        # Entry point
│   │   ├── api/           # API routes
│   │   ├── core/          # Configuration
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utilities
│   ├── src/               # Legacy ML code
│   ├── requirements.txt   # Python dependencies
│   └── run.py             # Run script
│
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── hooks/         # Custom hooks
│   │   └── utils/         # Utilities
│   ├── public/            # Static assets
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Vite configuration
│
├── models/                # Trained models
├── archive/               # Source domain data
├── Transferdata/          # Target domain data
├── results/               # Training results
│
├── mushroom_classification.ipynb  # Training notebook
├── README.md              # This file
└── STRUCTURE.md           # Detailed structure documentation
```

## Development

### Backend Development

```bash
cd backend
python run.py
```

Server sẽ tự động reload khi có thay đổi code (reload=True).

### Frontend Development

```bash
cd frontend
npm run dev
```

Hot Module Replacement (HMR) sẽ tự động reload khi có thay đổi.

### Build Production

**Backend:**
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run build
```

Output sẽ được tạo trong thư mục `frontend/dist/`.

## Testing

### Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# Model info
curl http://localhost:8000/api/v1/model/info

# Predict (cần file ảnh)
curl -X POST http://localhost:8000/api/v1/predict \
  -F "file=@path/to/image.jpg" \
  -F "top_k=3"
```

### Test Frontend

Mở trình duyệt và truy cập `http://localhost:3000`, upload ảnh và kiểm tra kết quả.

## Troubleshooting

### Backend không khởi động

- Kiểm tra Python version: `python --version` (cần 3.8+)
- Kiểm tra dependencies đã cài đặt: `pip list`
- Kiểm tra model có trong thư mục `models/` không

### Frontend không kết nối được Backend

- Kiểm tra Backend đang chạy tại `http://localhost:8000`
- Kiểm tra CORS configuration trong `backend/app/main.py`
- Kiểm tra API_BASE_URL trong `frontend/src/services/api.js`

### Model không load được

- Kiểm tra file model có trong `models/` không
- Kiểm tra model path trong `backend/app/core/config.py`
- Xem log trong terminal để biết lỗi cụ thể

### Prediction sai

- Kiểm tra model đang load đúng không (xem log khi khởi động)
- Kiểm tra số classes trong model có khớp với dataset không
- Đảm bảo ảnh đầu vào có chất lượng tốt và rõ ràng

## Lưu ý Quan trọng

**Hệ thống này chỉ mang tính chất tham khảo và phục vụ mục đích học tập.**

- Không nên dựa hoàn toàn vào kết quả để quyết định ăn nấm hoang dã
- Luôn tham khảo ý kiến chuyên gia trước khi sử dụng nấm hoang dã
- Một số loại nấm có thể gây tử vong nếu ăn nhầm
- Model có thể có độ chính xác không hoàn hảo, đặc biệt với ảnh chất lượng kém

## License

Dự án này được tạo cho mục đích học tập (Data Mining Project).

## Tài liệu Tham khảo

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [Vite Documentation](https://vitejs.dev/)

## Contributors

Data Mining Project Team
