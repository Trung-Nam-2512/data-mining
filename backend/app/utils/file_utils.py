"""
File utility functions
"""
from pathlib import Path
import tempfile
import shutil
from typing import BinaryIO


def save_uploaded_file(uploaded_file, suffix: str = None) -> Path:
    """
    Save uploaded file to temporary location
    
    Args:
        uploaded_file: FastAPI UploadFile
        suffix: File suffix (e.g., '.jpg')
    
    Returns:
        Path to temporary file
    """
    if suffix is None:
        suffix = Path(uploaded_file.filename).suffix if uploaded_file.filename else ".tmp"
    
    # Reset file pointer to beginning (important for FastAPI UploadFile)
    if hasattr(uploaded_file.file, 'seek'):
        uploaded_file.file.seek(0)
    
    # Create temporary file
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    
    try:
        # Copy file content
        shutil.copyfileobj(uploaded_file.file, tmp_file)
        tmp_file.flush()  # Ensure data is written
    except Exception as e:
        tmp_file.close()
        # Clean up on error
        Path(tmp_file.name).unlink(missing_ok=True)
        raise RuntimeError(f"Failed to save uploaded file: {str(e)}") from e
    finally:
        tmp_file.close()
        # Reset file pointer after reading
        if hasattr(uploaded_file.file, 'seek'):
            uploaded_file.file.seek(0)
    
    file_path = Path(tmp_file.name)
    
    # Verify file was created and has content
    if not file_path.exists() or file_path.stat().st_size == 0:
        file_path.unlink(missing_ok=True)
        raise RuntimeError("Saved file is empty or does not exist")
    
    return file_path


def cleanup_temp_file(file_path: Path) -> None:
    """Clean up temporary file"""
    if file_path.exists():
        file_path.unlink(missing_ok=True)

