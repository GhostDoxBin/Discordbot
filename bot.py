"""
Основной файл Discord бота для семьи Shinigami
"""

import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
from datetime import datetime
import asyncio

from utils.config import Config
from utils.logger import setup_logger
from database.family_db import FamilyDB

class ShinigamiBot(commands.Bot):
    """Главный класс бота"""
    
    def __init__(self, config: Config):
        intents = discord.Intents.all()
        intents.members = True
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=config.bot_prefix,
            intents=intents,
            help_command=None,
            chunk_guilds_at_startup=True
        )
        
        self.config = config
        self.logger = setup_logger()
        self.db = FamilyDB()
        
        self.start_time = datetime.now()
        self.guild = None
    
    async def setup_hook(self):
        """Настройка при запуске"""
        # Здесь можно загружать коги
        pass
    
    async def on_ready(self):
        """Событие при готовности"""
        print(f"\n{'=' * 60}")
        print(f"✅ БОТ {self.user} ЗАПУЩЕН!")
        print(f"🏮 Семья: {self.config.family_name}")
        print(f"🆔 ID: {self.user.id}")
        print(f"{'=' * 60}")
        
        self.logger.info(f"Бот {self.user} запущен")
        
        # Получаем сервер
        try:
            self.guild = self.get_guild(int(self.config.guild_id))
            if self.guild:
                self.logger.info(f"Сервер: {self.guild.name} (ID: {self.guild.id})")
        except:
            pass
        
        # Устанавливаем статус
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"семью {self.config.family_name}"
            )
        )
        
        # Регистрируем команды
        self.register_commands()
    
    def register_commands(self):
        """Регистрация команд"""
        
        @self.command(name="старт")
        async def start(ctx):
            embed = discord.Embed(
                title=f"🏮 Добро пожаловать в семью {self.config.family_name}!",
                description=f"Напишите `/` для меню или используйте команды с префиксом `{self.config.bot_prefix}`",
                color=self.config.hex_to_int(self.config.primary_color)
            )
            
            embed.add_field(
                name="📋 Основные команды:",
                value=f"• `{self.config.bot_prefix}статистика` - Статистика\n• `{self.config.bot_prefix}правила` - Правила\n• `{self.config.bot_prefix}члены` - Члены семьи\n• `{self.config.bot_prefix}профиль` - Ваш профиль",
                inline=False
            )
            
            if ctx.author.guild_permissions.administrator:
                embed.add_field(
                    name="⚙️ Админ команды:",
                    value=f"• `{self.config.bot_prefix}админ` - Админ панель\n• `{self.config.bot_prefix}заявки` - Заявки",
                    inline=False
                )
            
            await ctx.send(embed=embed)
    
    async def on_message(self, message):
        """Обработка всех сообщений"""
        if message.author == self.user:
            return
        
        # Если сообщение содержит только слэш - показываем меню
        if message.content.strip() == "/":
            await self.show_slash_menu(message)
            return
        
        await self.process_commands(message)
    
    async def show_slash_menu(self, message):
        """Показать меню при вводе /"""
        # Импортируем здесь чтобы избежать циклических импортов
        from ui.embeds import Embeds
        from ui.views import Views
        
        embeds = Embeds(self.config)
        views = Views(self)
        
        is_admin = message.author.guild_permissions.administrator
        
        # Получаем данные пользователя
        member_data = self.db.get_member(str(message.author.id))
        
        embed = embeds.startup_embed()
        if member_data:
            embed.add_field(
                name="👤 Ваш статус",
                value=f"🎖️ Ранг: {member_data.get('rank', 'Новичок')}",
                inline=False
            )
        
        view = views.main_menu_view(is_admin)
        
        await message.channel.send(embed=embed, view=view)
    
    async def on_command_error(self, ctx, error):
        """Обработка ошибок команд"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("⛔ У вас нет прав для выполнения этой команды!")
            return
        
        self.logger.error(f"Ошибка команды: {error}")
        await ctx.send(f"❌ Ошибка: {str(error)[:100]}...")
    
    async def start(self, token: str):
        """Запуск бота"""
        await super().start(token)