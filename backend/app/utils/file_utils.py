"""
File handling utilities
"""
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile

from app.config import settings
from app.utils.logger import logger


TEMP_UPLOAD_DIR = Path("./uploads/temp")
TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def save_uploaded_file(file: UploadFile) -> Path:
    """
    Save uploaded file to temporary directory
    
    Args:
        file: FastAPI UploadFile object
    
    Returns:
        Path to saved file
        
    Raises:
        ValueError: If file is invalid
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower().lstrip('.')
    if file_ext not in settings.allowed_extensions_list:
        raise ValueError(
            f"Định dạng file không hợp lệ. Chỉ chấp nhận: {', '.join(settings.allowed_extensions_list)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = TEMP_UPLOAD_DIR / unique_filename
    
    # Save file
    try:
        content = await file.read()
    
        # Validate file size
        if len(content) > settings.max_upload_size:
            raise ValueError(
                f"File quá lớn. Kích thước tối đa: {settings.max_upload_size / 1024 / 1024:.1f}MB"
            )
        
        if len(content) == 0:
            raise ValueError("File rỗng")
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"File uploaded successfully: {unique_filename}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error saving uploaded file: {str(e)}")
        raise


def cleanup_temp_file(file_path: Optional[Path]) -> None:
    """
    Clean up temporary file
    
    Args:
        file_path: Path to file to delete
    """
    if file_path and file_path.exists():
        try:
            file_path.unlink()
            logger.debug(f"Cleaned up temp file: {file_path.name}")
        except Exception as e:
            logger.warning(f"Failed to clean up temp file: {str(e)}")


def validate_image_file(file_path: Path) -> bool:
    """
    Validate if file is a valid image
    
    Args:
        file_path: Path to file
        
    Returns:
        True if valid, False otherwise
    """
    try:
        from PIL import Image
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception as e:
        logger.error(f"Invalid image file: {str(e)}")
        return False
