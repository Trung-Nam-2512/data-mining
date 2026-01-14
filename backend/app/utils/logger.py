"""
Logging configuration
"""
import logging
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger

from app.config import settings


def setup_logger(name: str = "mushroom_backend") -> logging.Logger:
    """
    Setup structured logging with JSON format
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with JSON format
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    json_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        timestamp=True
    )
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)
    
    return logger


# Global logger instance
logger = setup_logger()


