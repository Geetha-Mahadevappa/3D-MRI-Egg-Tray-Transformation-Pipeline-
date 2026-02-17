"""
Logging configuration for the MRI transformation pipeline.
Creates timestamped log files and logs to both console and file.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(name: str = "pipeline", log_dir: str | Path = "results/logs") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    log_dir = Path(log_dir)
    os.makedirs(log_dir, exist_ok=True)
    log_file = log_dir / "pipeline.log"

    # Automated Rotation: 5MB per file, keeping last 5 backups
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
