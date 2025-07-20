import logging
import os
from datetime import datetime
from .config import config

def setup_logging():
    """Setup application logging."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(config.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.log_file),
            logging.StreamHandler()
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('motor').setLevel(logging.INFO)

def get_logger(name: str) -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(name)

# Initialize logging on import
setup_logging()
