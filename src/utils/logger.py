"""
Configuração de logging do sistema
"""

import logging
import logging.handlers
import os
from datetime import datetime


def configurar_logger(log_level: str = "INFO"):
    """Configura sistema de logging"""

    os.makedirs("logs", exist_ok=True)

    level = getattr(logging, log_level.upper(), logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = f"logs/analysissupreme_{timestamp}.log"

    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    error_file = f"logs/analysissupreme_errors_{timestamp}.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"  # 5MB
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    logging.getLogger("ccxt").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    logging.info("Sistema de logging configurado")
