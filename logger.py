"""
Модуль логирования
"""

import logging
import sys
from datetime import datetime
import os

def setup_logger() -> logging.Logger:
    """Настройка логгера"""
    
    logger = logging.getLogger('shinigami_bot')
    logger.setLevel(logging.INFO)
    
    # Если уже настроен, возвращаем
    if logger.handlers:
        return logger
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Консольный хендлер
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Файловый хендлер
    try:
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.FileHandler(
            f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log',
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"⚠️ Не удалось создать файловый логгер: {e}")
    
    logger.addHandler(console_handler)
    
    # Отключаем лишние логи discord
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('discord.http').setLevel(logging.WARNING)
    
    return logger
