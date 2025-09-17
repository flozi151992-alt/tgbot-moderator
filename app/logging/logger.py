"""
Logging configuration for the Telegram bot.
"""
import logging
import os
from pathlib import Path

from app.config.settings import get_settings

def setup_logging():
    """Setup logging configuration."""
    settings = get_settings()
    
    # Create logs directory if it doesn't exist
    log_file_path = Path(settings.logging.file_path)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.logging.level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(settings.logging.file_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Set aiogram logging level to WARNING to reduce noise
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

def get_logger(name: str = __name__) -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(name)
