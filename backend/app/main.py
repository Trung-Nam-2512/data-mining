"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ORIGINS, API_V1_PREFIX
from app.core.settings import settings
from app.api.v1.api import api_router

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": settings.API_TITLE,
        "version": settings.API_VERSION,
        "endpoints": {
            "health": f"{API_V1_PREFIX}/health",
            "model_info": f"{API_V1_PREFIX}/model/info",
            "classes": f"{API_V1_PREFIX}/classes",
            "predict": f"{API_V1_PREFIX}/predict (POST)",
            "predict_batch": f"{API_V1_PREFIX}/predict/batch (POST)"
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

