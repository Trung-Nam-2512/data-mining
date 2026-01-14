"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path

from app.api.v1.router import api_router
from app.config import settings
from app.services.database import Database
from app.core.ensemble import get_ensemble_engine
from app.utils.logger import logger
from app import __version__


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("="*70)
    logger.info("Starting Mushroom Classification Backend API")
    logger.info("="*70)
    logger.info(f"Version: {__version__}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Port: {settings.server_port}")
    
    # Connect to MongoDB
    await Database.connect()
    
    # Load models (singleton pattern - loaded once)
    try:
        logger.info("Loading ensemble models...")
        engine = get_ensemble_engine()
        logger.info("✅ Ensemble engine initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load models: {str(e)}")
        logger.warning("API will start but predictions will fail!")
    
    logger.info("="*70)
    logger.info("API Ready!")
    logger.info("="*70)
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")
    await Database.disconnect()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Mushroom Classification API",
    description="""
    # Hệ thống Nhận diện Chi Nấm và Cảnh báo Độc tính
    
    API này sử dụng **Ensemble Learning (Soft Voting)** với 3 models:
    - ResNet-50 (91.59% accuracy)
    - EfficientNet-B0 (88.33% accuracy)
    - MobileNetV3-Large (87.64% accuracy)
    
    ## Features
    
    - 🍄 **Nhận diện 11 chi nấm** (9 Source Domain + 2 Target Domain)
    - ⚠️ **Cảnh báo độc tính tự động** (4 chi độc, 7 chi ăn được)
    - 🔬 **Grad-CAM visualization** để giải thích predictions
    - 📊 **Lưu lịch sử và thống kê** predictions
    - 🚀 **Batch prediction** (tối đa 5 ảnh)
    
    ## Độ chính xác
    
    - Ensemble Accuracy: ~93-94% (dự kiến)
    - Poisonous Detection Recall: ~90% (ưu tiên phát hiện nấm độc)
    
    ## Sử dụng
    
    1. Upload ảnh nấm qua `/api/v1/predict`
    2. Nhận kết quả với ensemble prediction + individual models
    3. Xem Grad-CAM visualization qua `/api/v1/gradcam`
    """,
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (không cần CORS restriction theo yêu cầu)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Serve static files from frontend build
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    logger.info(f"✅ Serving static files from: {static_dir}")
    
    # Mount assets directory (JS, CSS, images from Vite build)
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        logger.info(f"✅ Mounted /assets from {assets_dir}")
    
    # Serve index.html for React Router (catch-all for non-API routes)
    # This route must be registered last to catch all non-API routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        Serve React SPA - catch all routes that don't match API routes
        This allows React Router to handle client-side routing
        """
        # Skip API routes, docs, and assets (already handled by mounts)
        if (full_path.startswith("api/") or 
            full_path == "docs" or 
            full_path.startswith("docs/") or
            full_path == "redoc" or 
            full_path.startswith("redoc/") or 
            full_path == "openapi.json" or
            full_path.startswith("assets/") or
            full_path.startswith("static/")):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        
        # Check if it's a file request (has extension like .ico, .png, etc.)
        requested_path = static_dir / full_path
        if requested_path.is_file() and requested_path.exists():
            return FileResponse(str(requested_path))
        
        # Serve index.html for all other routes (React Router will handle routing)
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail="Frontend index.html not found")
else:
    logger.warning("⚠️ Static directory not found. Frontend will not be served.")
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Mushroom Classification API",
            "version": __version__,
            "docs": "/docs",
            "health": "/api/v1/health",
            "note": "Frontend not built. Static files not found."
        }


@app.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )
