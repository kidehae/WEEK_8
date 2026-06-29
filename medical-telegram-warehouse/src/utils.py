# src/utils.py
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load execution environments
load_dotenv()

def get_logger(name: str) -> logging.Logger:
    """Configures explicit logging to write file updates to logs/ directory."""
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        # File handler for auditing
        file_handler = logging.FileHandler(f"logs/scraping_{datetime.now().strftime('%Y%m%d')}.log", encoding="utf-8")
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler for immediate runtime telemetry
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(file_formatter)
        logger.addHandler(console_handler)
        
    return logger