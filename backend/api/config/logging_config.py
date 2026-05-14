import os
import logging
from logging.handlers import RotatingFileHandler


os.makedirs('logs', exist_ok=True)


def setup_logger(name: str = 'api') -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel('INFO')

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    )

    file_handler = RotatingFileHandler(
        'logs/api.log',
        maxBytes=5_000_000,
        backupCount=5,
        encoding='utf-8',
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger