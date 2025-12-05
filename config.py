"""
Модуль конфигурации бота
"""

import os
import sys
from dataclasses import dataclass
from typing import Optional

def safe_load_dotenv():
    """Безопасная загрузка .env файла"""
    try:
        from dotenv import load_dotenv
        
        # Пробуем загрузить .env файл
        env_path = '.env'
        if os.path.exists(env_path):
            print(f"📄 Найден .env файл: {env_path}")
            
            # Пробуем загрузить
            load_dotenv(env_path)
            print("✅ .env файл загружен")
            return True
        else:
            print("⚠️ .env файл не найден, использую переменные окружения")
            return True
            
    except Exception as e:
        print(f"⚠️ Ошибка загрузки .env: {e}")
        return False

# Загружаем .env
safe_load_dotenv()

@dataclass
class Config:
    """Класс конфигурации"""
    
    # Discord
    bot_token: str
    guild_id: str
    bot_prefix: str
    
    # Family
    family_name: str
    min_age: int
    min_level: int
    warn_limit: int
    
    # Channels (опционально)
    application_channel_id: Optional[str]
    log_channel_id: Optional[str]
    announcement_channel_id: Optional[str]
    general_channel_id: Optional[str]
    
    # Colors
    primary_color: str
    success_color: str
    warning_color: str
    danger_color: str
    info_color: str
    
    @classmethod
    def from_env(cls):
        """Загрузка из окружения"""
        def get_env(key: str, default: str = ""):
            value = os.getenv(key, default)
            if not value and key in ['DISCORD_BOT_TOKEN', 'DISCORD_GUILD_ID']:
                print(f"⚠️  Внимание: {key} не установлен")
            return value
        
        return cls(
            bot_token=get_env('DISCORD_BOT_TOKEN', ''),
            guild_id=get_env('DISCORD_GUILD_ID', ''),
            bot_prefix=get_env('BOT_PREFIX', '!'),
            family_name=get_env('FAMILY_NAME', 'Shinigami'),
            min_age=int(get_env('MIN_AGE', '14')),
            min_level=int(get_env('MIN_LEVEL', '3')),
            warn_limit=int(get_env('WARN_LIMIT', '5')),
            application_channel_id=get_env('APPLICATION_CHANNEL_ID'),
            log_channel_id=get_env('LOG_CHANNEL_ID'),
            announcement_channel_id=get_env('ANNOUNCEMENT_CHANNEL_ID'),
            general_channel_id=get_env('GENERAL_CHANNEL_ID'),
            primary_color=get_env('PRIMARY_COLOR', '#000000'),
            success_color=get_env('SUCCESS_COLOR', '#FFFFFF'),
            warning_color=get_env('WARNING_COLOR', '#FF0000'),
            danger_color=get_env('DANGER_COLOR', '#FF0000'),
            info_color=get_env('INFO_COLOR', '#800080')
        )
    
    def hex_to_int(self, hex_color: str) -> int:
        """Конвертация HEX цвета в int"""
        try:
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join(c * 2 for c in hex_color)
            return int(hex_color, 16)
        except:
            return 0x000000  # Черный по умолчанию

def load_config() -> Config:
    """Загрузка конфигурации"""
    print("🔄 Загрузка конфигурации...")
    
    config = Config.from_env()
    
    # Проверка обязательных полей
    if not config.bot_token:
        print("❌ ОШИБКА: DISCORD_BOT_TOKEN не установлен!")
        print("📝 Установите токен в .env файле:")
        print("DISCORD_BOT_TOKEN=ваш_токен_бота")
        sys.exit(1)
    
    print(f"✅ Конфигурация загружена")
    print(f"🏮 Семья: {config.family_name}")
    print(f"🔤 Префикс: {config.bot_prefix}")
    
    return config