"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Server Configuration
    server_host: str = Field(default="0.0.0.0", env="SERVER_HOST")
    server_port: int = Field(default=1356, env="SERVER_PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # MongoDB Configuration
    mongodb_url: str = Field(default="mongodb://mongodb:27017", env="MONGODB_URL")
    mongodb_db_name: str = Field(default="mushroom_classification", env="MONGODB_DB_NAME")
    
    # Model Configuration
    model_dir: Path = Field(default=Path("./models"), env="MODEL_DIR")
    resnet_model_path: Path = Field(
        default=Path("./models/best_model_resnet50_improved.pth"),
        env="RESNET_MODEL_PATH"
    )
    efficientnet_model_path: Path = Field(
        default=Path("./models/best_model_efficientnet_b0_improved.pth"),
        env="EFFICIENTNET_MODEL_PATH"
    )
    mobilenet_model_path: Path = Field(
        default=Path("./models/best_model_mobilenet_v3_large_improved.pth"),
        env="MOBILENET_MODEL_PATH"
    )
    
    # Upload Configuration
    max_upload_size: int = Field(default=10485760, env="MAX_UPLOAD_SIZE")  # 10MB
    max_batch_size: int = Field(default=5, env="MAX_BATCH_SIZE")
    allowed_extensions: str = Field(default="jpg,jpeg,png", env="ALLOWED_EXTENSIONS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Path = Field(default=Path("./logs/backend.log"), env="LOG_FILE")
    
    # Device Configuration
    device: str = Field(default="cuda", env="DEVICE")  # cuda or cpu
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def allowed_extensions_list(self) -> list:
        """Get allowed extensions as a list"""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]
    
    @property
    def model_paths(self) -> dict:
        """Get all model paths as a dictionary"""
        return {
            "resnet50": self.resnet_model_path,
            "efficientnet_b0": self.efficientnet_model_path,
            "mobilenet_v3_large": self.mobilenet_model_path
        }


# Global settings instance
settings = Settings()


