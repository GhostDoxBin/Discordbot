
"""
Embed сообщения для бота
"""

import discord
from datetime import datetime
from utils.config import Config

class Embeds:
    """Класс для создания embed сообщений"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def startup_embed(self) -> discord.Embed:
        """Embed при запуске"""
        embed = discord.Embed(
            title=f"🏮 Добро пожаловать в семью {self.config.family_name}!",
            description="Выберите действие из меню ниже:",
            color=self.config.hex_to_int(self.config.primary_color),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📋 Основные функции:",
            value="• 📊 Статистика семьи\n• 👥 Список членов\n• 📜 Правила\n• 📅 События\n• 👤 Профиль",
            inline=False
        )
        
        embed.add_field(
            name="📨 Для вступления:",
            value="Нажмите '📋 Подать заявку' в меню",
            inline=False
        )
        
        embed.set_footer(text="Используйте / для вызова меню")
        return embed
    
    def error_embed(self, title: str, description: str) -> discord.Embed:
        """Embed для ошибок"""
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=self.config.hex_to_int(self.config.danger_color)
        )
        return embed
    
    def success_embed(self, title: str, description: str) -> discord.Embed:
        """Embed для успешных действий"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=self.config.hex_to_int(self.config.success_color)
        )
        return embed
    
    def warning_embed(self, title: str, description: str) -> discord.Embed:
        """Embed для предупреждений"""
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=self.config.hex_to_int(self.config.warning_color)
        )
        return embed
    
    def info_embed(self, title: str, description: str) -> discord.Embed:
        """Embed для информации"""
        embed = discord.Embed(
            title=f"ℹ️ {title}",
            description=description,
            color=self.config.hex_to_int(self.config.info_color)
        )
        return embed
    
    def profile_embed(self, member: discord.Member, member_data: dict) -> discord.Embed:
        """Embed профиля"""
        embed = discord.Embed(
            title=f"👤 Профиль {member.display_name}",
            color=member.color if member.color != discord.Color.default() else self.config.hex_to_int(self.config.primary_color),
            timestamp=datetime.now()
        )
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        embed.add_field(name="🎮 Игровой ник", value=member_data.get('game_name', 'Не указан'), inline=True)
        embed.add_field(name="🎖️ Ранг", value=member_data.get('rank', 'Новичок'), inline=True)
        embed.add_field(name="📅 В семье с", value=member_data.get('join_date', 'Недавно')[:10], inline=True)
        embed.add_field(name="🆔 Discord ID", value=member.id, inline=True)
        
        return embed