"""
ПОЛНОСТЬЮ РАБОЧИЙ DISCORD БОТ SHINIGAMI С ВСЕМИ ФУНКЦИЯМИ
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import Button, View, Modal, TextInput, Select
import json
import os
from datetime import datetime, timedelta
import asyncio
from typing import Optional
import random

print("=" * 60)
print("🤖 DISCORD БОТ SHINIGAMI - ПОЛНЫЙ ФУНКЦИОНАЛ")
print("=" * 60)

# Настройки
TOKEN = "MTQ0NjEzMjc1Nzg1NTA3NjUyNw.GEnPhX.jye5IMrWS9dsX3IyvUXWQct1VkGfDEKXpyXx7Q"
FAMILY_NAME = "Shinigami"
GUILD_ID = 1446133863708360706  # ID вашего сервера
BOT_ID = 1446132757855076527    # ID вашего бота

print(f"🏮 Семья: {FAMILY_NAME}")
print(f"🔗 Ссылка для приглашения:")
print(f"https://discord.com/api/oauth2/authorize?client_id={BOT_ID}&permissions=8&scope=bot%20applications.commands")
print("=" * 60)

# ========== БАЗА ДАННЫХ ==========

class SimpleDB:
    def __init__(self):
        self.data = {
            'members': {},
            'applications': {},
            'warnings': {},
            'events': {},
            'ranks': {
                'rank_1': {'name': 'Глава', 'color': '#000000', 'permissions': 'Все'},
                'rank_2': {'name': 'Заместитель', 'color': '#FF0000', 'permissions': 'Высокие'},
                'rank_3': {'name': 'Советник', 'color': '#800080', 'permissions': 'Средние'},
                'rank_4': {'name': 'Боец', 'color': '#FFFFFF', 'permissions': 'Базовые'},
                'rank_5': {'name': 'Новичок', 'color': '#00FF00', 'permissions': 'Минимальные'}
            }
        }
        self.load_from_file()
    
    def save_to_file(self):
        """Сохранить данные в файл"""
        try:
            with open('shinigami_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")
    
    def load_from_file(self):
        """Загрузить данные из файла"""
        try:
            if os.path.exists('shinigami_data.json'):
                with open('shinigami_data.json', 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                print("✅ Данные загружены из файла")
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
    
    def get_member(self, user_id: str):
        return self.data['members'].get(str(user_id))
    
    def add_member(self, user_id: str, data: dict):
        self.data['members'][str(user_id)] = data
        self.save_to_file()
    
    def update_member(self, user_id: str, data: dict):
        user_id = str(user_id)
        if user_id in self.data['members']:
            self.data['members'][user_id].update(data)
            self.save_to_file()
    
    def add_application(self, user_id: str, data: dict):
        self.data['applications'][str(user_id)] = data
        self.save_to_file()
    
    def get_pending_applications(self):
        return [app for app in self.data['applications'].values() if app.get('status') == 'pending']
    
    def add_warning(self, user_id: str, admin_id: str, reason: str, warning_id: int = None):
        user_id = str(user_id)
        if user_id not in self.data['warnings']:
            self.data['warnings'][user_id] = []
        
        if warning_id is None:
            warning_id = len(self.data['warnings'][user_id]) + 1
        
        self.data['warnings'][user_id].append({
            'id': warning_id,
            'reason': reason,
            'admin_id': admin_id,
            'date': datetime.now().isoformat()
        })
        self.save_to_file()
    
    def remove_warning(self, user_id: str, warning_id: int):
        user_id = str(user_id)
        if user_id in self.data['warnings']:
            new_warnings = []
            found = False
            for w in self.data['warnings'][user_id]:
                if w.get('id') == warning_id:
                    found = True
                else:
                    new_warnings.append(w)
            
            if found:
                self.data['warnings'][user_id] = new_warnings
                self.save_to_file()
                return True
        return False
    
    def add_event(self, event_id: str, data: dict):
        self.data['events'][event_id] = data
        self.save_to_file()
    
    def update_event(self, event_id: str, data: dict):
        if event_id in self.data['events']:
            self.data['events'][event_id].update(data)
            self.save_to_file()
    
    def remove_event(self, event_id: str):
        if event_id in self.data['events']:
            del self.data['events'][event_id]
            self.save_to_file()
            return True
        return False
    
    def add_rank(self, rank_id: str, data: dict):
        self.data['ranks'][rank_id] = data
        self.save_to_file()
    
    def update_rank(self, rank_id: str, data: dict):
        if rank_id in self.data['ranks']:
            self.data['ranks'][rank_id].update(data)
            self.save_to_file()
    
    def remove_rank(self, rank_id: str):
        if rank_id in self.data['ranks']:
            del self.data['ranks'][rank_id]
            self.save_to_file()
            return True
        return False
    
    def get_rank_by_name(self, rank_name: str):
        for rank_id, rank_data in self.data['ranks'].items():
            if rank_data.get('name') == rank_name:
                return rank_id, rank_data
        return None, None
    
    def get_all_ranks(self):
        return self.data['ranks']

# ========== БОТ ==========

intents = discord.Intents.all()
intents.members = True
intents.message_content = True

class ShinigamiBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        self.db = SimpleDB()
    
    async def setup_hook(self):
        """Настройка при запуске"""
        try:
            # Синхронизируем команды с сервером
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print("✅ Слэш-команды синхронизированы!")
        except Exception as e:
            print(f"⚠️ Ошибка синхронизации команд: {e}")
        
        # Запускаем фоновые задачи
        self.check_events.start()
        print("✅ Фоновые задачи запущены!")
    
    @tasks.loop(minutes=5)
    async def check_events(self):
        """Проверка предстоящих мероприятий"""
        try:
            now = datetime.now()
            
            for event_id, event in self.db.data['events'].items():
                event_date_str = event.get('date', '')
                if event_date_str:
                    try:
                        event_date = datetime.strptime(event_date_str, '%d.%m.%Y %H:%M')
                        
                        # Проверяем, наступило ли время мероприятия
                        time_diff = (event_date - now).total_seconds()
                        
                        # Уведомляем за 1 час до мероприятия
                        if 0 < time_diff <= 3600 and not event.get('notified'):
                            for guild in self.guilds:
                                # Ищем канал для анонсов
                                announcement_channel = discord.utils.get(guild.text_channels, name="мероприятия")
                                if not announcement_channel:
                                    announcement_channel = discord.utils.get(guild.text_channels, name="анонсы")
                                
                                if announcement_channel:
                                    embed = discord.Embed(
                                        title="⏰ МЕРОПРИЯТИЕ ЧЕРЕЗ 1 ЧАС!",
                                        description=f"**{event.get('title', 'Мероприятие')}** начнется через 1 час!",
                                        color=0xFFA500,
                                        timestamp=now
                                    )
                                    
                                    embed.add_field(name="📅 Время", value=event_date_str, inline=True)
                                    embed.add_field(name="📍 Место", value=event.get('location', 'Не указано'), inline=True)
                                    embed.add_field(name="📝 Описание", value=event.get('description', '')[:200], inline=False)
                                    
                                    await announcement_channel.send(embed=embed)
                                    
                                    # Помечаем, что уведомление отправлено
                                    self.db.update_event(event_id, {'notified': True})
                                    break
                    except:
                        continue
        except Exception as e:
            print(f"Ошибка в проверке мероприятий: {e}")
    
    @check_events.before_loop
    async def before_check_events(self):
        """Ожидание перед запуском проверки мероприятий"""
        await self.wait_until_ready()

bot = ShinigamiBot()

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

async def create_discord_role(guild: discord.Guild, rank_name: str, color_hex: str = "#000000"):
    """Создать роль в Discord"""
    try:
        # Конвертируем HEX в цвет Discord
        if color_hex.startswith('#'):
            color_hex = color_hex[1:]
        
        try:
            color = discord.Color(int(color_hex, 16))
        except:
            color = discord.Color.default()
        
        # Создаем роль
        role = await guild.create_role(
            name=rank_name,
            color=color,
            mentionable=True,
            reason=f"Ранг для семьи {FAMILY_NAME}"
        )
        return role
    except Exception as e:
        print(f"❌ Ошибка создания роли {rank_name}: {e}")
        return None

async def assign_role_to_member(member: discord.Member, rank_name: str, guild: discord.Guild):
    """Назначить роль участнику"""
    try:
        # Ищем существующую роль
        role = discord.utils.get(guild.roles, name=rank_name)
        
        # Если роль не существует, создаем ее
        if not role:
            # Получаем цвет ранга из базы
            rank_id, rank_data = bot.db.get_rank_by_name(rank_name)
            color_hex = rank_data.get('color', '#000000') if rank_data else '#000000'
            role = await create_discord_role(guild, rank_name, color_hex)
        
        if role:
            # Удаляем все другие ранговые роли
            rank_names = [data['name'] for data in bot.db.get_all_ranks().values()]
            for other_rank in rank_names:
                if other_rank != rank_name:
                    other_role = discord.utils.get(guild.roles, name=other_rank)
                    if other_role and other_role in member.roles:
                        await member.remove_roles(other_role)
            
            # Добавляем новую роль
            await member.add_roles(role)
            return True
    except Exception as e:
        print(f"❌ Ошибка назначения роли {rank_name} пользователю {member}: {e}")
    return False

async def mention_all_members(guild: discord.Guild, event_title: str, channel: discord.TextChannel):
    """Упомянуть всех членов семьи по мероприятию"""
    try:
        # Получаем всех членов семьи из базы
        members_to_mention = []
        for user_id in bot.db.data['members']:
            member = guild.get_member(int(user_id))
            if member:
                members_to_mention.append(member.mention)
        
        if members_to_mention:
            # Ограничиваем количество упоминаний (Discord лимит)
            mentions = " ".join(members_to_mention[:50])  # Максимум 50 упоминаний
            
            embed = discord.Embed(
                title=f"📢 УВЕДОМЛЕНИЕ О МЕРОПРИЯТИИ: {event_title}",
                description=f"Внимание всем членам семьи {FAMILY_NAME}!",
                color=0xFFA500,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="🎯 Важное мероприятие",
                value=f"Пожалуйста, ознакомьтесь с информацией выше и примите участие!",
                inline=False
            )
            
            await channel.send(f"{mentions}", embed=embed)
            return True
    except Exception as e:
        print(f"❌ Ошибка упоминания участников: {e}")
    return False

# ========== МОДАЛЬНЫЕ ОКНА ==========

class ApplicationModal(Modal, title=f"📋 Заявка в {FAMILY_NAME}"):
    def __init__(self):
        super().__init__(timeout=None)
        
        self.age = TextInput(
            label="Ваш возраст",
            placeholder="Введите возраст (от 14 лет)",
            required=True,
            max_length=3
        )
        
        self.level = TextInput(
            label="Уровень в игре",
            placeholder="Введите уровень (от 3)",
            required=True,
            max_length=3
        )
        
        self.game_name = TextInput(
            label="Игровой ник",
            placeholder="Введите ваш игровой никнейм",
            required=True,
            max_length=50
        )
        
        self.experience = TextInput(
            label="Игровой опыт",
            placeholder="Расскажите о вашем игровом опыте...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        
        self.reason = TextInput(
            label="Почему хотите вступить?",
            placeholder="Почему хотите вступить в нашу семью?",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        
        self.add_item(self.age)
        self.add_item(self.level)
        self.add_item(self.game_name)
        self.add_item(self.experience)
        self.add_item(self.reason)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            age = int(self.age.value)
            level = int(self.level.value)
            game_name = self.game_name.value
            experience = self.experience.value
            reason = self.reason.value
            
            # Проверяем возраст
            if age < 14:
                await interaction.followup.send(
                    "❌ Минимальный возраст для вступления - 14 лет!",
                    ephemeral=True
                )
                return
            
            # Проверяем уровень
            if level < 3:
                await interaction.followup.send(
                    "❌ Минимальный уровень для вступления - 3!",
                    ephemeral=True
                )
                return
            
            # Сохраняем заявку
            bot.db.add_application(str(interaction.user.id), {
                'username': str(interaction.user),
                'full_name': interaction.user.display_name,
                'discord_id': interaction.user.id,
                'age': age,
                'level': level,
                'game_name': game_name,
                'experience': experience,
                'reason': reason,
                'status': 'pending',
                'application_date': datetime.now().isoformat()
            })
            
            # Отправляем подтверждение
            embed = discord.Embed(
                title="✅ Заявка отправлена!",
                description=f"Спасибо за заявку, {interaction.user.mention}!",
                color=0x00FF00,
                timestamp=datetime.now()
            )
            
            embed.add_field(name="🎮 Игровой ник", value=game_name, inline=True)
            embed.add_field(name="🎂 Возраст", value=str(age), inline=True)
            embed.add_field(name="🎮 Уровень", value=str(level), inline=True)
            embed.add_field(name="📝 Причина", value=reason[:200], inline=False)
            
            embed.set_footer(text="Ожидайте рассмотрения заявки администрацией")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Уведомляем администраторов
            await notify_admins_about_application(interaction)
            
        except ValueError:
            await interaction.followup.send(
                "❌ Неверный формат возраста или уровня!",
                ephemeral=True
            )
        except Exception as e:
            print(f"Ошибка обработки заявки: {e}")
            await interaction.followup.send(
                "❌ Произошла ошибка при отправке заявки!",
                ephemeral=True
            )

async def notify_admins_about_application(interaction: discord.Interaction):
    """Уведомление администраторов о новой заявке"""
    try:
        app = bot.db.data['applications'].get(str(interaction.user.id))
        if not app:
            return
        
        embed = discord.Embed(
            title="📨 НОВАЯ ЗАЯВКА НА ВСТУПЛЕНИЕ!",
            description=f"Пользователь {interaction.user.mention} подал заявку в семью!",
            color=0xFFA500,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="🎮 Игровой ник", value=app.get('game_name', 'Не указан'), inline=True)
        embed.add_field(name="🎂 Возраст", value=str(app.get('age', 0)), inline=True)
        embed.add_field(name="🎮 Уровень", value=str(app.get('level', 0)), inline=True)
        embed.add_field(name="📝 Опыт", value=app.get('experience', '')[:200] or "Не указан", inline=False)
        embed.add_field(name="💭 Причина", value=app.get('reason', '')[:200] or "Не указана", inline=False)
        
        embed.add_field(
            name="⚡ Быстрые действия:",
            value=f"• `/принять @{interaction.user.name}` - Принять заявку\n• `/отклонить @{interaction.user.name} причина` - Отклонить заявку",
            inline=False
        )
        
        # Ищем канал для заявок
        apps_channel = discord.utils.get(interaction.guild.text_channels, name="заявки")
        if apps_channel:
            await apps_channel.send(embed=embed)
        else:
            # Или отправляем в канал администраторов
            admin_channel = discord.utils.get(interaction.guild.text_channels, name="админ")
            if admin_channel:
                await admin_channel.send(embed=embed)
            else:
                # Или отправляем в первый доступный канал с правами на отправку
                for channel in interaction.guild.text_channels:
                    if channel.permissions_for(interaction.guild.me).send_messages:
                        await channel.send(f"@everyone 📨 Новая заявка!", embed=embed)
                        break
            
    except Exception as e:
        print(f"Ошибка уведомления админов: {e}")

class CreateEventModal(Modal, title="📅 Создание мероприятия"):
    def __init__(self):
        super().__init__(timeout=None)
        
        self.title = TextInput(
            label="Название мероприятия",
            placeholder="Введите название мероприятия",
            required=True,
            max_length=100
        )
        
        self.description = TextInput(
            label="Описание",
            placeholder="Опишите мероприятие...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        
        self.date = TextInput(
            label="Дата и время (ДД.ММ.ГГГГ ЧЧ:ММ)",
            placeholder="Например: 25.12.2024 20:00",
            required=True,
            max_length=20
        )
        
        self.location = TextInput(
            label="Место проведения",
            placeholder="Где будет проходить мероприятие?",
            required=True,
            max_length=200
        )
        
        self.add_item(self.title)
        self.add_item(self.description)
        self.add_item(self.date)
        self.add_item(self.location)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            title = self.title.value
            description = self.description.value
            date_str = self.date.value
            location = self.location.value
            
            # Проверяем формат даты
            try:
                datetime.strptime(date_str, '%d.%m.%Y %H:%M')
            except ValueError:
                await interaction.followup.send(
                    "❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ ЧЧ:ММ",
                    ephemeral=True
                )
                return
            
            # Создаем ID для мероприятия
            event_id = f"event_{int(datetime.now().timestamp())}"
            
            # Добавляем мероприятие в базу
            bot.db.add_event(event_id, {
                'title': title,
                'description': description,
                'date': date_str,
                'location': location,
                'created_by': str(interaction.user),
                'created_at': datetime.now().isoformat(),
                'participants': []
            })
            
            # Отправляем подтверждение
            embed = discord.Embed(
                title="✅ Мероприятие создано!",
                description=f"Мероприятие **{title}** успешно создано!",
                color=0x00FF00,
                timestamp=datetime.now()
            )
            
            embed.add_field(name="📅 Дата и время", value=date_str, inline=True)
            embed.add_field(name="📍 Место", value=location, inline=True)
            embed.add_field(name="📝 Описание", value=description[:500], inline=False)
            embed.set_footer(text=f"Создал: {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Отправляем анонс в канал
            announcement_embed = discord.Embed(
                title=f"📢 НОВОЕ МЕРОПРИЯТИЕ: {title}",
                description=f"Внимание всем членам семьи {FAMILY_NAME}!",
                color=0xFFA500,
                timestamp=datetime.now()
            )
            
            announcement_embed.add_field(name="📅 Когда", value=date_str, inline=True)
            announcement_embed.add_field(name="📍 Где", value=location, inline=True)
            announcement_embed.add_field(name="📝 Описание", value=description[:500], inline=False)
            announcement_embed.set_footer(text=f"Организатор: {interaction.user.display_name}")
            
            # Ищем канал для анонсов
            announcement_channel = discord.utils.get(interaction.guild.text_channels, name="мероприятия")
            if not announcement_channel:
                announcement_channel = discord.utils.get(interaction.guild.text_channels, name="анонсы")
            if announcement_channel:
                await announcement_channel.send(embed=announcement_embed)
            else:
                await interaction.channel.send(embed=announcement_embed)
            
        except Exception as e:
            print(f"Ошибка создания мероприятия: {e}")
            await interaction.followup.send(
                "❌ Произошла ошибка при создании мероприятия!",
                ephemeral=True
            )

class EditEventModal(Modal):
    def __init__(self, current_event: dict):
        super().__init__(title="✏️ Редактирование мероприятия", timeout=None)
        
        self.title = TextInput(
            label="Название мероприятия",
            placeholder="Введите название мероприятия",
            default=current_event.get('title', ''),
            required=True,
            max_length=100
        )
        
        self.description = TextInput(
            label="Описание",
            placeholder="Опишите мероприятие...",
            style=discord.TextStyle.paragraph,
            default=current_event.get('description', ''),
            required=True,
            max_length=1000
        )
        
        self.date = TextInput(
            label="Дата и время (ДД.ММ.ГГГГ ЧЧ:ММ)",
            placeholder="Например: 25.12.2024 20:00",
            default=current_event.get('date', ''),
            required=True,
            max_length=20
        )
        
        self.location = TextInput(
            label="Место проведения",
            placeholder="Где будет проходить мероприятие?",
            default=current_event.get('location', ''),
            required=True,
            max_length=200
        )
        
        self.add_item(self.title)
        self.add_item(self.description)
        self.add_item(self.date)
        self.add_item(self.location)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            title = self.title.value
            description = self.description.value
            date_str = self.date.value
            location = self.location.value
            
            # Проверяем формат даты
            try:
                datetime.strptime(date_str, '%d.%m.%Y %H:%M')
            except ValueError:
                await interaction.followup.send(
                    "❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ ЧЧ:ММ",
                    ephemeral=True
                )
                return
            
            # Ищем мероприятие для обновления
            event_found = None
            event_id_found = None
            for event_id, event_data in bot.db.data['events'].items():
                if event_found is None:
                    event_found = event_data
                    event_id_found = event_id
                    break
            
            if not event_found:
                await interaction.followup.send(
                    "❌ Мероприятие не найдено!",
                    ephemeral=True
                )
                return
            
            # Обновляем мероприятие
            bot.db.update_event(event_id_found, {
                'title': title,
                'description': description,
                'date': date_str,
                'location': location,
                'updated_by': str(interaction.user),
                'updated_at': datetime.now().isoformat()
            })
            
            # Отправляем подтверждение
            embed = discord.Embed(
                title="✅ Мероприятие обновлено!",
                description=f"Мероприятие успешно обновлено!",
                color=0x00FF00,
                timestamp=datetime.now()
            )
            
            embed.add_field(name="📅 Дата и время", value=date_str, inline=True)
            embed.add_field(name="📍 Место", value=location, inline=True)
            embed.add_field(name="📝 Описание", value=description[:500], inline=False)
            embed.set_footer(text=f"Обновил: {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"Ошибка редактирования мероприятия: {e}")
            await interaction.followup.send(
                "❌ Произошла ошибка при редактировании мероприятия!",
                ephemeral=True
            )

class CreateRankModal(Modal, title="🎖️ Создание ранга"):
    def __init__(self):
        super().__init__(timeout=None)
        
        self.name = TextInput(
            label="Название ранга",
            placeholder="Введите название ранга",
            required=True,
            max_length=50
        )
        
        self.color = TextInput(
            label="Цвет (HEX формат)",
            placeholder="Например: #FF0000 для красного",
            default="#000000",
            required=True,
            max_length=7
        )
        
        self.permissions = TextInput(
            label="Описание прав",
            placeholder="Опишите права этого ранга...",
            style=discord.TextStyle.paragraph,
            default="Базовые права",
            required=True,
            max_length=500
        )
        
        self.add_item(self.name)
        self.add_item(self.color)
        self.add_item(self.permissions)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            name = self.name.value
            color = self.color.value
            permissions = self.permissions.value
            
            # Проверяем HEX цвет
            if not color.startswith('#') or len(color) != 7:
                await interaction.followup.send(
                    "❌ Неверный формат цвета! Используйте HEX формат, например #FF0000",
                    ephemeral=True
                )
                return
            
            # Проверяем, существует ли уже ранг с таким именем
            for existing_rank in bot.db.data['ranks'].values():
                if existing_rank.get('name', '').lower() == name.lower():
                    await interaction.followup.send(
                        f"❌ Ранг с названием '{name}' уже существует!",
                        ephemeral=True
                    )
                    return
            
            # Создаем новый ID для ранга
            rank_id = f"rank_{len(bot.db.data['ranks']) + 1}"
            
            # Добавляем ранг в базу
            bot.db.add_rank(rank_id, {
                'name': name,
                'color': color,
                'permissions': permissions,
                'created_by': str(interaction.user),
                'created_at': datetime.now().isoformat()
            })
            
            # Создаем роль в Discord
            role = await create_discord_role(interaction.guild, name, color)
            
            # Отправляем подтверждение
            embed = discord.Embed(
                title="✅ Ранг создан!",
                description=f"Ранг **{name}** успешно создан!",
                color=0x00FF00,
                timestamp=datetime.now()
            )
            
            embed.add_field(name="🎨 Цвет", value=color, inline=True)
            embed.add_field(name="🔧 Права", value=permissions[:200], inline=False)
            embed.add_field(name="👑 Роль Discord", value="✅ Создана" if role else "❌ Не создана", inline=True)
            embed.set_footer(text=f"Создал: {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"Ошибка создания ранга: {e}")
            await interaction.followup.send(
                "❌ Произошла ошибка при создании ранга!",
                ephemeral=True
            )

class EditRankModal(Modal):
    def __init__(self, rank_name: str):
        super().__init__(title="✏️ Редактирование ранга", timeout=None)
        
        rank_id, rank_data = bot.db.get_rank_by_name(rank_name)
        self.rank_id = rank_id
        self.old_name = rank_name
        
        self.name = TextInput(
            label="Название ранга",
            placeholder="Введите название ранга",
            default=rank_data.get('name', '') if rank_data else '',
            required=True,
            max_length=50
        )
        
        self.color = TextInput(
            label="Цвет (HEX формат)",
            placeholder="Например: #FF0000 для красного",
            default=rank_data.get('color', '#000000') if rank_data else '#000000',
            required=True,
            max_length=7
        )
        
        self.permissions = TextInput(
            label="Описание прав",
            placeholder="Опишите права этого ранга...",
            style=discord.TextStyle.paragraph,
            default=rank_data.get('permissions', 'Базовые права') if rank_data else 'Базовые права',
            required=True,
            max_length=500
        )
        
        self.add_item(self.name)
        self.add_item(self.color)
        self.add_item(self.permissions)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            name = self.name.value
            color = self.color.value
            permissions = self.permissions.value
            
            if not self.rank_id:
                await interaction.followup.send(
                    "❌ Ранг не найден!",
                    ephemeral=True
                )
                return
            
            # Проверяем HEX цвет
            if not color.startswith('#') or len(color) != 7:
                await interaction.followup.send(
                    "❌ Неверный формат цвета! Используйте HEX формат, например #FF0000",
                    ephemeral=True
                )
                return
            
            old_rank_data = bot.db.data['ranks'][self.rank_id]
            old_name = old_rank_data.get('name', '')
            
            # Проверяем, не меняется ли название на уже существующее (кроме текущего)
            if name.lower() != old_name.lower():
                for rid, rank_data in bot.db.data['ranks'].items():
                    if rid != self.rank_id and rank_data.get('name', '').lower() == name.lower():
                        await interaction.followup.send(
                            f"❌ Ранг с названием '{name}' уже существует!",
                            ephemeral=True
                        )
                        return
            
            # Обновляем ранг
            bot.db.update_rank(self.rank_id, {
                'name': name,
                'color': color,
                'permissions': permissions,
                'updated_by': str(interaction.user),
                'updated_at': datetime.now().isoformat()
            })
            
            # Обновляем роль в Discord если название изменилось
            if name != old_name:
                try:
                    old_role = discord.utils.get(interaction.guild.roles, name=old_name)
                    if old_role:
                        discord_color = discord.Color(int(color.lstrip('#'), 16))
                        await old_role.edit(name=name, color=discord_color)
                except Exception as e:
                    print(f"Ошибка обновления роли: {e}")
            
            # Отправляем подтверждение
            embed = discord.Embed(
                title="✅ Ранг обновлен!",
                description=f"Ранг **{old_name}** успешно обновлен!",
                color=0x00FF00,
                timestamp=datetime.now()
            )
            
            embed.add_field(name="📝 Новое название", value=name, inline=True)
            embed.add_field(name="🎨 Новый цвет", value=color, inline=True)
            embed.add_field(name="🔧 Новые права", value=permissions[:200], inline=False)
            embed.set_footer(text=f"Обновил: {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"Ошибка редактирования ранга: {e}")
            await interaction.followup.send(
                "❌ Произошла ошибка при редактировании ранга!",
                ephemeral=True
            )

# ========== СЛЭШ-КОМАНДЫ ДЛЯ ВСЕХ ==========

@bot.tree.command(
    name="заявка",
    description="Подать заявку на вступление в семью Shinigami"
)
async def apply_slash(interaction: discord.Interaction):
    """Слэш-команда подачи заявки"""
    # Проверяем, не является ли уже членом
    if bot.db.get_member(str(interaction.user.id)):
        await interaction.response.send_message(
            "✅ Вы уже член семьи!",
            ephemeral=True
        )
        return
    
    # Проверяем, не подана ли уже заявка
    existing_app = bot.db.data['applications'].get(str(interaction.user.id))
    if existing_app and existing_app.get('status') == 'pending':
        await interaction.response.send_message(
            "📝 Ваша заявка уже на рассмотрении!",
            ephemeral=True
        )
        return
    
    # Открываем модальное окно
    modal = ApplicationModal()
    await interaction.response.send_modal(modal)

@bot.tree.command(
    name="старт",
    description="Главное меню семьи Shinigami"
)
async def start_slash(interaction: discord.Interaction):
    """Слэш-команда старта"""
    embed = discord.Embed(
        title=f"🏮 Добро пожаловать в семью {FAMILY_NAME}!",
        description=f"Используйте `/` для вызова меню или команды ниже",
        color=0x000000
    )
    
    embed.add_field(
        name="📋 Основные команды:",
        value="• `/заявка` - Подать заявку\n• `/статистика` - Статистика семьи\n• `/правила` - Правила семьи\n• `/члены` - Список членов\n• `/профиль` - Ваш профиль\n• `/мой_ранг` - Ваш ранг\n• `/ранги` - Все ранги\n• `/события` - Мероприятия",
        inline=False
    )
    
    if interaction.user.guild_permissions.administrator:
        embed.add_field(
            name="⚙️ Админ команды:",
            value="• `/админ` - Админ панель\n• `/управление_рангами` - Управление рангами\n• `/управление_мероприятиями` - Управление мероприятиями",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="статистика",
    description="Статистика семьи Shinigami"
)
async def stats_slash(interaction: discord.Interaction):
    """Слэш-команда статистики"""
    members = len(bot.db.data['members'])
    apps = len(bot.db.get_pending_applications())
    warns = sum(len(w) for w in bot.db.data['warnings'].values())
    events = len(bot.db.data['events'])
    ranks = len(bot.db.data['ranks'])
    
    embed = discord.Embed(
        title=f"📊 Статистика семьи {FAMILY_NAME}",
        color=0x800080,
        timestamp=datetime.now()
    )
    
    embed.add_field(name="👥 Членов", value=str(members), inline=True)
    embed.add_field(name="📨 Заявок", value=str(apps), inline=True)
    embed.add_field(name="⚠️ Варнов", value=str(warns), inline=True)
    embed.add_field(name="🎖️ Рангов", value=str(ranks), inline=True)
    embed.add_field(name="📅 Событий", value=str(events), inline=True)
    
    # Распределение по рангам
    rank_counts = {}
    for member in bot.db.data['members'].values():
        rank = member.get('rank', 'Новичок')
        rank_counts[rank] = rank_counts.get(rank, 0) + 1
    
    if rank_counts:
        rank_stats = "\n".join([f"  {rank}: {count}" for rank, count in rank_counts.items()])
        embed.add_field(
            name="🎖️ Распределение по рангам:",
            value=f"```{rank_stats}```",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="правила",
    description="Правила семьи Shinigami"
)
async def rules_slash(interaction: discord.Interaction):
    """Слэш-команда правил"""
    embed = discord.Embed(
        title=f"📜 Правила семьи {FAMILY_NAME}",
        color=0xFF0000
    )
    
    rules_text = """
**Основные принципы:**
1. Уважение к членам семьи
2. Активность в игре и чате  
3. Помощь новичкам
4. Исполнение приказов руководства

**Иерархия:**
👑 Койбу (Глава)
🎖️ Вакагасира (Заместитель)
⭐ Сятей (Советник)
⚔️ Солдат (Боец)
🌱 Кохай (Новичок)

**Требования для вступления:**
• Возраст от 14 лет
• Уровень персонажа от 3
• Хорошая активность
• Адекватность
"""
    
    embed.description = rules_text
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="члены",
    description="Список членов семьи Shinigami"
)
async def members_slash(interaction: discord.Interaction):
    """Слэш-команда списка членов"""
    if not bot.db.data['members']:
        await interaction.response.send_message("👥 В семье пока нет членов.")
        return
    
    embed = discord.Embed(
        title=f"👥 Члены семьи {FAMILY_NAME}",
        color=0x800080
    )
    
    members_list = list(bot.db.data['members'].items())
    
    for i, (user_id, member) in enumerate(members_list[:15], 1):
        try:
            discord_member = interaction.guild.get_member(int(user_id))
            if discord_member:
                name = discord_member.display_name
            else:
                name = member.get('game_name', 'Без имени')
            
            embed.add_field(
                name=f"{i}. {name}",
                value=f"🎖️ {member.get('rank', 'Новичок')} | 🎮 Ур. {member.get('level', 0)}",
                inline=False
            )
        except:
            continue
    
    if len(members_list) > 15:
        embed.set_footer(text=f"Показано 15 из {len(members_list)} членов")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="профиль",
    description="Просмотр профиля участника"
)
@app_commands.describe(участник="Участник для просмотра профиля (необязательно)")
async def profile_slash(interaction: discord.Interaction, участник: discord.Member = None):
    """Слэш-команда профиля"""
    target = участник or interaction.user
    member_data = bot.db.get_member(str(target.id))
    
    embed = discord.Embed(
        title=f"👤 Профиль {target.display_name}",
        color=target.color if target.color != discord.Color.default() else 0x000000,
        timestamp=datetime.now()
    )
    
    if target.avatar:
        embed.set_thumbnail(url=target.avatar.url)
    
    if member_data:
        embed.add_field(name="🎮 Игровой ник", value=member_data.get('game_name', 'Не указан'), inline=True)
        embed.add_field(name="🎖️ Ранг", value=member_data.get('rank', 'Новичок'), inline=True)
        
        join_date = member_data.get('join_date', '')
        if join_date:
            try:
                date_obj = datetime.fromisoformat(join_date.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%d.%m.%Y')
                embed.add_field(name="📅 В семье с", value=formatted_date, inline=True)
            except:
                embed.add_field(name="📅 В семье с", value="Недавно", inline=True)
        else:
            embed.add_field(name="📅 В семье с", value="Недавно", inline=True)
            
        embed.add_field(name="🎂 Возраст", value=str(member_data.get('age', 0)), inline=True)
        embed.add_field(name="🎮 Уровень", value=str(member_data.get('level', 0)), inline=True)
    else:
        embed.description = "❌ Не является членом семьи"
    
    embed.add_field(name="🆔 Discord ID", value=target.id, inline=True)
    
    # Добавляем информацию о предупреждениях
    warnings = bot.db.data['warnings'].get(str(target.id), [])
    if warnings:
        warning_list = "\n".join([f"{w['id']}. {w['reason']} ({w['date'][:10]})" for w in warnings[:3]])
        embed.add_field(
            name="⚠️ Предупреждения",
            value=f"Всего: {len(warnings)}\n```{warning_list}```",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="ранги",
    description="Ранги семьи Shinigami"
)
async def ranks_slash(interaction: discord.Interaction):
    """Слэш-команда рангов"""
    embed = discord.Embed(
        title=f"🎖️ Ранги семьи {FAMILY_NAME}",
        color=0x00FF00
    )
    
    ranks = bot.db.data['ranks']
    for rank_id, rank_data in ranks.items():
        embed.add_field(
            name=f"{rank_data['name']}",
            value=f"Цвет: {rank_data['color']}\nПрава: {rank_data.get('permissions', 'Базовые')}",
            inline=True
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="мой_ранг",
    description="Показать ваш текущий ранг в семье"
)
async def myrank_slash(interaction: discord.Interaction):
    """Слэш-команда моего ранга"""
    member_data = bot.db.get_member(str(interaction.user.id))
    
    if not member_data:
        await interaction.response.send_message(
            "❌ Вы не являетесь членом семьи.",
            ephemeral=True
        )
        return
    
    rank = member_data.get('rank', 'Новичок')
    
    # Получаем информацию о ранге
    rank_id, rank_data = bot.db.get_rank_by_name(rank)
    
    embed = discord.Embed(
        title=f"🎖️ Ваш ранг: {rank}",
        color=0x00FF00
    )
    
    if rank_data:
        embed.add_field(name="Цвет", value=rank_data.get('color', '#000000'), inline=True)
        embed.add_field(name="Права", value=rank_data.get('permissions', 'Базовые'), inline=True)
    
    if rank == "Глава":
        embed.description = "👑 У вас полный доступ ко всем функциям!"
    elif rank == "Заместитель":
        embed.description = "🎖️ Вы можете управлять членами и заявками."
    elif rank == "Советник":
        embed.description = "⭐ Вы можете управлять заявками и модерировать."
    elif rank == "Боец":
        embed.description = "⚔️ Вы можете просматривать статистику и участвовать в событиях."
    else:
        embed.description = "🌱 Вы новичок в семье. Активно участвуйте в жизни семьи для повышения!"
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="события",
    description="Показать ближайшие события семьи"
)
async def events_slash(interaction: discord.Interaction):
    """Слэш-команда событий"""
    events = bot.db.data['events']
    
    if not events:
        await interaction.response.send_message("📭 Нет запланированных событий.")
        return
    
    # Фильтруем только будущие события
    future_events = {}
    for event_id, event in events.items():
        event_date_str = event.get('date', '')
        try:
            event_date = datetime.strptime(event_date_str, '%d.%m.%Y %H:%M')
            if event_date > datetime.now():
                future_events[event_id] = event
        except:
            future_events[event_id] = event
    
    if not future_events:
        await interaction.response.send_message("📭 Нет предстоящих событий.")
        return
    
    embed = discord.Embed(
        title=f"📅 События семьи {FAMILY_NAME}",
        color=0x800080,
        timestamp=datetime.now()
    )
    
    future_events_list = list(future_events.items())
    
    for i, (event_id, event) in enumerate(future_events_list[:5], 1):
        embed.add_field(
            name=f"{i}. {event.get('title', 'Без названия')}",
            value=f"📅 **Когда:** {event.get('date', 'Дата не указана')}\n📍 **Где:** {event.get('location', 'Место не указано')}\n📝 **Описание:** {event.get('description', 'Без описания')[:100]}...",
            inline=False
        )
    
    if len(future_events_list) > 5:
        embed.set_footer(text=f"Показано 5 из {len(future_events_list)} событий")
    
    await interaction.response.send_message(embed=embed)

# ========== АДМИН КОМАНДЫ ==========

@bot.tree.command(
    name="админ",
    description="Админ панель семьи Shinigami"
)
@app_commands.default_permissions(administrator=True)
async def admin_slash(interaction: discord.Interaction):
    """Слэш-команда админ панели"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    members = len(bot.db.data['members'])
    apps = len(bot.db.get_pending_applications())
    warns = sum(len(w) for w in bot.db.data['warnings'].values())
    events = len(bot.db.data['events'])
    ranks = len(bot.db.data['ranks'])
    
    embed = discord.Embed(
        title=f"⚙️ Админ панель {FAMILY_NAME}",
        color=0xFF0000,
        timestamp=datetime.now()
    )
    
    embed.add_field(name="👥 Членов", value=str(members), inline=True)
    embed.add_field(name="📨 Заявок", value=str(apps), inline=True)
    embed.add_field(name="⚠️ Варнов", value=str(warns), inline=True)
    embed.add_field(name="🎖️ Рангов", value=str(ranks), inline=True)
    embed.add_field(name="📅 Событий", value=str(events), inline=True)
    
    embed.add_field(
        name="📋 Управление заявками:",
        value="• `/заявки` - Просмотр заявок\n• `/принять` - Принять заявку\n• `/отклонить` - Отклонить заявку",
        inline=False
    )
    
    embed.add_field(
        name="⚖️ Управление членами:",
        value="• `/предупредить` - Выдать варн\n• `/снять_предупреждение` - Снять варн\n• `/изменить_ранг` - Изменить ранг",
        inline=False
    )
    
    embed.add_field(
        name="🎖️ Управление рангами:",
        value="• `/управление_рангами` - Управление рангами\n• `/создать_ранг` - Создать ранг\n• `/редактировать_ранг` - Редактировать ранг\n• `/удалить_ранг` - Удалить ранг",
        inline=False
    )
    
    embed.add_field(
        name="📅 Управление мероприятиями:",
        value="• `/управление_мероприятиями` - Управление мероприятиями\n• `/создать_мероприятие` - Создать мероприятие\n• `/редактировать_мероприятие` - Редактировать мероприятие\n• `/удалить_мероприятие` - Удалить мероприятие\n• `/тегнуть_по_мероприятию` - Тегнуть всех",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="заявки",
    description="Просмотр заявок на вступление"
)
@app_commands.default_permissions(administrator=True)
async def applications_slash(interaction: discord.Interaction):
    """Слэш-команда просмотра заявок"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    apps = bot.db.get_pending_applications()
    
    if not apps:
        await interaction.response.send_message("📭 Нет заявок на рассмотрении.")
        return
    
    embed = discord.Embed(
        title="📨 Заявки на рассмотрении",
        color=0xFFA500
    )
    
    for i, app in enumerate(apps[:5], 1):
        embed.add_field(
            name=f"{i}. {app.get('full_name', app.get('username', 'Без имени'))}",
            value=f"🎂 Возраст: {app.get('age')}\n🎮 Уровень: {app.get('level')}\n🎮 Ник: {app.get('game_name')}\n📝 Причина: {app.get('reason', '')[:50]}...",
            inline=False
        )
    
    if len(apps) > 5:
        embed.set_footer(text=f"Всего заявок: {len(apps)}")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="принять",
    description="Принять заявку на вступление"
)
@app_commands.describe(
    участник="Участник для принятия в семью",
    ранг="Ранг для нового члена"
)
@app_commands.choices(ранг=[
    app_commands.Choice(name="Новичок", value="Новичок"),
    app_commands.Choice(name="Боец", value="Боец"),
    app_commands.Choice(name="Советник", value="Советник"),
    app_commands.Choice(name="Заместитель", value="Заместитель"),
    app_commands.Choice(name="Глава", value="Глава")
])
@app_commands.default_permissions(administrator=True)
async def accept_slash(interaction: discord.Interaction, участник: discord.Member, ранг: app_commands.Choice[str]):
    """Слэш-команда принятия заявки"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    user_id = str(участник.id)
    applications = bot.db.data['applications']
    
    # Если нет активной заявки, все равно можно принять
    if user_id not in applications or applications[user_id].get('status') != 'pending':
        # Проверяем, не является ли уже членом
        if bot.db.get_member(user_id):
            await interaction.response.send_message("❌ Этот пользователь уже член семьи!", ephemeral=True)
            return
        
        # Создаем "заявку" на лету
        application = {
            'username': str(участник),
            'full_name': участник.display_name,
            'game_name': участник.display_name,
            'level': 1,
            'age': 18
        }
    else:
        application = applications[user_id]
    
    rank_value = ранг.value
    
    # Добавляем в члены
    bot.db.add_member(user_id, {
        'user_id': user_id,
        'username': application.get('username', ''),
        'full_name': application.get('full_name', ''),
        'game_name': application.get('game_name', ''),
        'rank': rank_value,
        'join_date': datetime.now().isoformat(),
        'level': application.get('level', 1),
        'age': application.get('age', 18),
        'accepted_by': str(interaction.user)
    })
    
    # Обновляем статус заявки если она была
    if user_id in applications:
        applications[user_id]['status'] = 'accepted'
    
    # Создаем и назначаем роль
    role_assigned = await assign_role_to_member(участник, rank_value, interaction.guild)
    
    embed = discord.Embed(
        title="✅ Заявка принята",
        description=f"Пользователь {участник.mention} принят в семью!",
        color=0x00FF00
    )
    
    embed.add_field(name="🎖️ Ранг", value=rank_value, inline=True)
    embed.add_field(name="✅ Принял", value=interaction.user.display_name, inline=True)
    embed.add_field(name="👑 Роль", value="✅ Назначена" if role_assigned else "⚠️ Не назначена", inline=True)
    
    await interaction.response.send_message(embed=embed)
    
    # Уведомляем пользователя
    try:
        await участник.send(f"🎉 Поздравляем! Вы приняты в семью {FAMILY_NAME}!\nВаш ранг: {rank_value}")
    except:
        pass

@bot.tree.command(
    name="отклонить",
    description="Отклонить заявку на вступление"
)
@app_commands.describe(
    участник="Участник для отклонения заявки",
    причина="Причина отклонения"
)
@app_commands.default_permissions(administrator=True)
async def reject_slash(interaction: discord.Interaction, участник: discord.Member, причина: str):
    """Слэш-команда отклонения заявки"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    user_id = str(участник.id)
    applications = bot.db.data['applications']
    
    if user_id not in applications or applications[user_id].get('status') != 'pending':
        await interaction.response.send_message("❌ Заявка не найдена или уже рассмотрена!", ephemeral=True)
        return
    
    # Обновляем статус заявки
    applications[user_id]['status'] = 'rejected'
    applications[user_id]['reject_reason'] = причина
    
    embed = discord.Embed(
        title="❌ Заявка отклонена",
        description=f"Заявка пользователя {участник.mention} отклонена.",
        color=0xFF0000
    )
    
    embed.add_field(name="📝 Причина", value=причина, inline=False)
    
    await interaction.response.send_message(embed=embed)
    
    # Уведомляем пользователя
    try:
        await участник.send(f"😔 Ваша заявка в семью {FAMILY_NAME} отклонена.\n**Причина:** {причина}")
    except:
        pass

@bot.tree.command(
    name="предупредить",
    description="Выдать предупреждение участнику"
)
@app_commands.describe(
    участник="Участник для выдачи предупреждения",
    причина="Причина предупреждения"
)
@app_commands.default_permissions(administrator=True)
async def warn_slash(interaction: discord.Interaction, участник: discord.Member, причина: str):
    """Слэш-команда выдачи предупреждения"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    # Проверяем является ли участник членом
    if not bot.db.get_member(str(участник.id)):
        await interaction.response.send_message(f"❌ {участник.mention} не является членом семьи!", ephemeral=True)
        return
    
    # Добавляем предупреждение
    warnings_count = len(bot.db.data['warnings'].get(str(участник.id), []))
    bot.db.add_warning(str(участник.id), str(interaction.user.id), причина, warnings_count + 1)
    
    # Считаем количество предупреждений
    warnings = bot.db.data['warnings'].get(str(участник.id), [])
    warn_count = len(warnings)
    
    embed = discord.Embed(
        title="⚠️ Предупреждение выдано",
        description=f"{участник.mention} получил предупреждение!",
        color=0xffa500
    )
    
    embed.add_field(name="Причина", value=причина, inline=False)
    embed.add_field(name="ID предупреждения", value=str(warnings_count + 1), inline=True)
    embed.add_field(name="Всего предупреждений", value=str(warn_count), inline=True)
    embed.add_field(name="Выдал", value=interaction.user.display_name, inline=True)
    
    await interaction.response.send_message(embed=embed)
    
    # Отправляем личное сообщение
    try:
        await участник.send(f"⚠️ Вы получили предупреждение на сервере **{interaction.guild.name}**\n**Причина:** {причина}\n**ID предупреждения:** {warnings_count + 1}\n**Всего предупреждений:** {warn_count}")
    except:
        pass

@bot.tree.command(
    name="снять_предупреждение",
    description="Снять предупреждение с участника"
)
@app_commands.describe(
    участник="Участник для снятия предупреждения",
    id_предупреждения="ID предупреждения для снятия"
)
@app_commands.default_permissions(administrator=True)
async def remove_warning_slash(interaction: discord.Interaction, участник: discord.Member, id_предупреждения: int):
    """Слэш-команда снятия предупреждения"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    # Проверяем является ли участник членом
    if not bot.db.get_member(str(участник.id)):
        await interaction.response.send_message(f"❌ {участник.mention} не является членом семьи!", ephemeral=True)
        return
    
    # Удаляем предупреждение
    success = bot.db.remove_warning(str(участник.id), id_предупреждения)
    
    if success:
        warnings = bot.db.data['warnings'].get(str(участник.id), [])
        warn_count = len(warnings)
        
        embed = discord.Embed(
            title="✅ Предупреждение снято",
            description=f"Предупреждение #{id_предупреждения} снято с {участник.mention}!",
            color=0x00FF00
        )
        
        embed.add_field(name="Оставшееся предупреждений", value=str(warn_count), inline=True)
        embed.add_field(name="Снял", value=interaction.user.display_name, inline=True)
        
        await interaction.response.send_message(embed=embed)
        
        # Уведомляем пользователя
        try:
            await участник.send(f"✅ Предупреждение #{id_предупреждения} снято с вас на сервере **{interaction.guild.name}**\n**Снял:** {interaction.user.display_name}\n**Осталось предупреждений:** {warn_count}")
        except:
            pass
    else:
        await interaction.response.send_message(f"❌ Предупреждение #{id_предупреждения} не найдено у {участник.mention}!", ephemeral=True)

@bot.tree.command(
    name="изменить_ранг",
    description="Изменить ранг участника"
)
@app_commands.describe(
    участник="Участник для изменения ранга",
    новый_ранг="Новый ранг для участника"
)
@app_commands.choices(новый_ранг=[
    app_commands.Choice(name="Новичок", value="Новичок"),
    app_commands.Choice(name="Боец", value="Боец"),
    app_commands.Choice(name="Советник", value="Советник"),
    app_commands.Choice(name="Заместитель", value="Заместитель"),
    app_commands.Choice(name="Глава", value="Глава")
])
@app_commands.default_permissions(administrator=True)
async def change_rank_slash(interaction: discord.Interaction, участник: discord.Member, новый_ранг: app_commands.Choice[str]):
    """Слэш-команда изменения ранга"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    user_id = str(участник.id)
    
    # Проверяем является ли участник членом
    member_data = bot.db.get_member(user_id)
    if not member_data:
        await interaction.response.send_message(f"❌ {участник.mention} не является членом семьи!", ephemeral=True)
        return
    
    old_rank = member_data.get('rank', 'Новичок')
    new_rank = новый_ранг.value
    
    # Обновляем ранг в базе
    bot.db.update_member(user_id, {'rank': new_rank})
    
    # Назначаем новую роль
    role_assigned = await assign_role_to_member(участник, new_rank, interaction.guild)
    
    embed = discord.Embed(
        title="🎖️ Ранг изменен",
        description=f"Ранг {участник.mention} изменен!",
        color=0x800080
    )
    
    embed.add_field(name="Старый ранг", value=old_rank, inline=True)
    embed.add_field(name="Новый ранг", value=new_rank, inline=True)
    embed.add_field(name="👑 Роль", value="✅ Назначена" if role_assigned else "⚠️ Не назначена", inline=True)
    embed.add_field(name="Изменил", value=interaction.user.display_name, inline=True)
    
    await interaction.response.send_message(embed=embed)
    
    # Уведомляем пользователя
    try:
        await участник.send(f"🎖️ Ваш ранг в семье {FAMILY_NAME} изменен!\n**Было:** {old_rank}\n**Стало:** {new_rank}\n**Изменил:** {interaction.user.display_name}")
    except:
        pass

# ========== УПРАВЛЕНИЕ РАНГАМИ ==========

@bot.tree.command(
    name="управление_рангами",
    description="Панель управления рангами"
)
@app_commands.default_permissions(administrator=True)
async def manage_ranks_slash(interaction: discord.Interaction):
    """Слэш-команда управления рангами"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🎖️ Управление рангами",
        description="Выберите действие:",
        color=0x800080
    )
    
    embed.add_field(
        name="Доступные команды:",
        value="• `/создать_ранг` - Создать новый ранг\n• `/редактировать_ранг` - Редактировать существующий ранг\n• `/удалить_ранг` - Удалить ранг\n• `/ранги` - Просмотр всех рангов",
        inline=False
    )
    
    # Показываем текущие ранги
    ranks = bot.db.data['ranks']
    if ranks:
        rank_list = "\n".join([f"• **{data['name']}** - {data.get('permissions', 'Базовые')}" for data in ranks.values()])
        embed.add_field(name="Текущие ранги:", value=rank_list, inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="создать_ранг",
    description="Создать новый ранг"
)
@app_commands.default_permissions(administrator=True)
async def create_rank_slash(interaction: discord.Interaction):
    """Слэш-команда создания ранга"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    modal = CreateRankModal()
    await interaction.response.send_modal(modal)

@bot.tree.command(
    name="редактировать_ранг",
    description="Редактировать существующий ранг"
)
@app_commands.describe(
    ранг="Ранг для редактирования"
)
@app_commands.default_permissions(administrator=True)
async def edit_rank_slash(interaction: discord.Interaction, ранг: str):
    """Слэш-команда редактирования ранга"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    # Ищем ранг
    rank_id, rank_data = bot.db.get_rank_by_name(ранг)
    
    if not rank_data:
        # Показываем список доступных рангов
        available_ranks = [r['name'] for r in bot.db.data['ranks'].values()]
        await interaction.response.send_message(
            f"❌ Ранг '{ранг}' не найден! Доступные ранги: {', '.join(available_ranks)}",
            ephemeral=True
        )
        return
    
    # Открываем модальное окно с текущими данными
    modal = EditRankModal(ранг)
    await interaction.response.send_modal(modal)

@bot.tree.command(
    name="удалить_ранг",
    description="Удалить ранг"
)
@app_commands.describe(
    ранг="Ранг для удаления"
)
@app_commands.default_permissions(administrator=True)
async def delete_rank_slash(interaction: discord.Interaction, ранг: str):
    """Слэш-команда удаления ранга"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    # Ищем ранг
    rank_id, rank_data = bot.db.get_rank_by_name(ранг)
    
    if not rank_data:
        # Показываем список доступных рангов
        available_ranks = [r['name'] for r in bot.db.data['ranks'].values()]
        await interaction.response.send_message(
            f"❌ Ранг '{ранг}' не найден! Доступные ранги: {', '.join(available_ranks)}",
            ephemeral=True
        )
        return
    
    # Проверяем, используется ли ранг кем-то
    used_by = []
    for user_id, member_data in bot.db.data['members'].items():
        if member_data.get('rank') == ранг:
            try:
                member = interaction.guild.get_member(int(user_id))
                if member:
                    used_by.append(member.display_name)
            except:
                used_by.append(f"ID: {user_id}")
    
    if used_by:
        await interaction.response.send_message(
            f"❌ Невозможно удалить ранг '{ранг}', так как он используется:\n" + "\n".join([f"• {name}" for name in used_by[:5]]),
            ephemeral=True
        )
        return
    
    # Удаляем ранг из базы
    success = bot.db.remove_rank(rank_id)
    
    if success:
        # Пытаемся удалить роль из Discord
        try:
            role = discord.utils.get(interaction.guild.roles, name=ранг)
            if role:
                await role.delete(reason=f"Удаление ранга {ранг}")
        except Exception as e:
            print(f"Ошибка удаления роли: {e}")
        
        embed = discord.Embed(
            title="✅ Ранг удален",
            description=f"Ранг '{ранг}' успешно удален!",
            color=0x00FF00
        )
        
        embed.add_field(name="Удалил", value=interaction.user.display_name, inline=True)
        
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"❌ Ошибка при удалении ранга '{ранг}'!", ephemeral=True)

# ========== УПРАВЛЕНИЕ МЕРОПРИЯТИЯМИ ==========

@bot.tree.command(
    name="управление_мероприятиями",
    description="Панель управления мероприятиями"
)
@app_commands.default_permissions(administrator=True)
async def manage_events_slash(interaction: discord.Interaction):
    """Слэш-команда управления мероприятиями"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    events = bot.db.data['events']
    
    embed = discord.Embed(
        title="📅 Управление мероприятиями",
        description="Выберите действие:",
        color=0x800080,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="Доступные команды:",
        value="• `/создать_мероприятие` - Создать новое мероприятие\n• `/редактировать_мероприятие` - Редактировать мероприятие\n• `/удалить_мероприятие` - Удалить мероприятие\n• `/тегнуть_по_мероприятию` - Тегнуть всех участников\n• `/события` - Просмотр всех мероприятий",
        inline=False
    )
    
    # Показываем текущие мероприятия
    if events:
        event_list = "\n".join([f"• **{data['title']}** - {data.get('date', 'Дата не указана')}" for data in list(events.values())[:5]])
        embed.add_field(name="Текущие мероприятия:", value=event_list, inline=False)
        embed.set_footer(text=f"Всего мероприятий: {len(events)}")
    else:
        embed.add_field(name="Текущие мероприятия:", value="📭 Нет запланированных мероприятий", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="создать_мероприятие",
    description="Создать новое мероприятие"
)
@app_commands.default_permissions(administrator=True)
async def create_event_slash(interaction: discord.Interaction):
    """Слэш-команда создания мероприятия"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    modal = CreateEventModal()
    await interaction.response.send_modal(modal)

@bot.tree.command(
    name="редактировать_мероприятие",
    description="Редактировать мероприятие"
)
@app_commands.default_permissions(administrator=True)
async def edit_event_slash(interaction: discord.Interaction):
    """Слэш-команда редактирования мероприятия"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    events = bot.db.data['events']
    
    if not events:
        await interaction.response.send_message("📭 Нет мероприятий для редактирования!", ephemeral=True)
        return
    
    # Создаем выпадающий список мероприятий
    class EventSelect(Select):
        def __init__(self):
            options = []
            for event_id, event_data in list(events.items())[:25]:  # Ограничиваем 25 опциями
                options.append(
                    discord.SelectOption(
                        label=event_data.get('title', 'Без названия')[:100],
                        description=event_data.get('date', 'Без даты'),
                        value=event_id
                    )
                )
            
            super().__init__(
                placeholder="Выберите мероприятие для редактирования...",
                options=options,
                max_values=1
            )
        
        async def callback(self, interaction: discord.Interaction):
            event_id = self.values[0]
            event_data = events.get(event_id)
            
            if event_data:
                modal = EditEventModal(event_data)
                await interaction.response.send_modal(modal)
            else:
                await interaction.response.send_message("❌ Мероприятие не найдено!", ephemeral=True)
    
    class EventSelectView(View):
        def __init__(self):
            super().__init__(timeout=60)
            self.add_item(EventSelect())
    
    embed = discord.Embed(
        title="✏️ Редактирование мероприятия",
        description="Выберите мероприятие из списка:",
        color=0x800080
    )
    
    view = EventSelectView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(
    name="удалить_мероприятие",
    description="Удалить мероприятие"
)
@app_commands.describe(
    мероприятие="Название мероприятия для удаления"
)
@app_commands.default_permissions(administrator=True)
async def delete_event_slash(interaction: discord.Interaction, мероприятие: str):
    """Слэш-команда удаления мероприятия"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    # Ищем мероприятие
    event_found = None
    event_id_found = None
    
    for event_id, event_data in bot.db.data['events'].items():
        if event_data.get('title') == мероприятие:
            event_found = event_data
            event_id_found = event_id
            break
    
    if not event_found:
        # Показываем список доступных мероприятий
        available_events = [e['title'] for e in bot.db.data['events'].values()]
        if available_events:
            await interaction.response.send_message(
                f"❌ Мероприятие '{мероприятие}' не найдено! Доступные мероприятия: {', '.join(available_events[:5])}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Мероприятие не найдено! Нет доступных мероприятий.",
                ephemeral=True
            )
        return
    
    # Удаляем мероприятие из базы
    success = bot.db.remove_event(event_id_found)
    
    if success:
        embed = discord.Embed(
            title="✅ Мероприятие удалено",
            description=f"Мероприятие '{мероприятие}' успешно удалено!",
            color=0x00FF00
        )
        
        embed.add_field(name="Удалил", value=interaction.user.display_name, inline=True)
        embed.add_field(name="Дата", value=event_found.get('date', 'Не указана'), inline=True)
        
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"❌ Ошибка при удалении мероприятия '{мероприятие}'!", ephemeral=True)

@bot.tree.command(
    name="тегнуть_по_мероприятию",
    description="Тегнуть всех участников по мероприятию"
)
@app_commands.describe(
    мероприятие="Название мероприятия для тега",
    канал="Канал для отправки уведомления (необязательно)"
)
@app_commands.default_permissions(administrator=True)
async def mention_event_slash(interaction: discord.Interaction, мероприятие: str, канал: discord.TextChannel = None):
    """Слэш-команда тега по мероприятию"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    # Ищем мероприятие
    event_found = None
    
    for event_data in bot.db.data['events'].values():
        if event_data.get('title') == мероприятие:
            event_found = event_data
            break
    
    if not event_found:
        # Показываем список доступных мероприятий
        available_events = [e['title'] for e in bot.db.data['events'].values()]
        await interaction.response.send_message(
            f"❌ Мероприятие '{мероприятие}' не найдено! Доступные мероприятия: {', '.join(available_events[:5])}",
            ephemeral=True
        )
        return
    
    # Определяем канал для отправки
    target_channel = канал or interaction.channel
    
    # Отправляем уведомление
    await interaction.response.send_message(f"📢 Отправляю уведомление о мероприятии '{мероприятие}'...", ephemeral=True)
    
    # Тегнем всех участников
    success = await mention_all_members(interaction.guild, мероприятие, target_channel)
    
    if success:
        await interaction.followup.send(f"✅ Уведомление о мероприятии '{мероприятие}' отправлено в канал {target_channel.mention}!", ephemeral=True)
    else:
        await interaction.followup.send(f"⚠️ Не удалось отправить уведомление о мероприятии '{мероприятие}'!", ephemeral=True)

# ========== СОБЫТИЯ БОТА ==========

@bot.event
async def on_ready():
    print(f"\n{'=' * 60}")
    print(f"✅ БОТ {bot.user} ЗАПУЩЕН!")
    print(f"🆔 ID: {bot.user.id}")
    print(f"🏮 Семья: {FAMILY_NAME}")
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print(f"{'=' * 60}")
    
    # Устанавливаем статус бота
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"семью {FAMILY_NAME}"
        ),
        status=discord.Status.online
    )
    
    print("✅ Бот готов к работе!")
    print(f"{'=' * 60}")

@bot.event
async def on_member_join(member: discord.Member):
    """Приветствие новых участников"""
    try:
        embed = discord.Embed(
            title=f"👋 Добро пожаловать в семью {FAMILY_NAME}!",
            description=f"Приветствуем тебя, {member.mention} на нашем сервере!",
            color=0x00FF00,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📋 Для начала:",
            value=f"1. Используй `/заявка` для вступления в семью\n2. Прочти `/правила`\n3. Познакомься с `/членами`",
            inline=False
        )
        
        embed.add_field(
            name="🔗 Полезные команды:",
            value="• `/старт` - Главное меню\n• `/правила` - Правила сервера\n• `/ранги` - Система рангов",
            inline=False
        )
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        # Ищем канал приветствий
        welcome_channel = discord.utils.get(member.guild.text_channels, name="приветствия")
        if welcome_channel:
            await welcome_channel.send(embed=embed)
        else:
            # Или отправляем в первый доступный канал
            for channel in member.guild.text_channels:
                if channel.permissions_for(member.guild.me).send_messages:
                    await channel.send(f"👋 {member.mention}, добро пожаловать!", embed=embed)
                    break
        
        # Отправляем личное сообщение
        try:
            welcome_dm = discord.Embed(
                title=f"🏮 Добро пожаловать в семью {FAMILY_NAME}!",
                description=f"Приветствуем тебя на нашем сервере!",
                color=0x800080
            )
            
            welcome_dm.add_field(
                name="📋 Первые шаги:",
                value="1. Прочти правила в канале #правила\n2. Подай заявку командой `/заявка`\n3. Познакомься с другими участниками",
                inline=False
            )
            
            welcome_dm.add_field(
                name="🔗 Полезные команды:",
                value="• `/старт` - Главное меню\n• `/заявка` - Подать заявку\n• `/правила` - Правила семьи\n• `/ранги` - Система рангов",
                inline=False
            )
            
            await member.send(embed=welcome_dm)
        except:
            pass  # Нельзя отправить ЛС
            
    except Exception as e:
        print(f"Ошибка при приветствии {member}: {e}")

# ========== КОМАНДЫ ДЛЯ ТЕСТИРОВАНИЯ ==========

@bot.tree.command(
    name="тест",
    description="Тестовая команда для проверки бота"
)
async def test_slash(interaction: discord.Interaction):
    """Тестовая команда"""
    embed = discord.Embed(
        title="🧪 Тест системы",
        description="Бот работает корректно! ✅",
        color=0x00FF00,
        timestamp=datetime.now()
    )
    
    embed.add_field(name="🏮 Семья", value=FAMILY_NAME, inline=True)
    embed.add_field(name="🤖 Бот", value=bot.user.name, inline=True)
    embed.add_field(name="📊 Задержка", value=f"{round(bot.latency * 1000)}мс", inline=True)
    embed.add_field(name="👥 Участников", value=str(len(bot.db.data['members'])), inline=True)
    embed.add_field(name="📨 Заявок", value=str(len(bot.db.get_pending_applications())), inline=True)
    embed.add_field(name="📅 Событий", value=str(len(bot.db.data['events'])), inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="сброс",
    description="Сбросить все данные (только для разработки)"
)
@app_commands.default_permissions(administrator=True)
async def reset_slash(interaction: discord.Interaction):
    """Сброс всех данных"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    # Создаем кнопки для подтверждения
    class ResetConfirmView(View):
        def __init__(self):
            super().__init__(timeout=30)
        
        @discord.ui.button(label="✅ Да, сбросить всё", style=discord.ButtonStyle.danger)
        async def confirm(self, interaction: discord.Interaction, button: Button):
            # Сбрасываем все данные
            bot.db.data = {
                'members': {},
                'applications': {},
                'warnings': {},
                'events': {},
                'ranks': {
                    'rank_1': {'name': 'Глава', 'color': '#000000', 'permissions': 'Все'},
                    'rank_2': {'name': 'Заместитель', 'color': '#FF0000', 'permissions': 'Высокие'},
                    'rank_3': {'name': 'Советник', 'color': '#800080', 'permissions': 'Средние'},
                    'rank_4': {'name': 'Боец', 'color': '#FFFFFF', 'permissions': 'Базовые'},
                    'rank_5': {'name': 'Новичок', 'color': '#00FF00', 'permissions': 'Минимальные'}
                }
            }
            bot.db.save_to_file()
            
            await interaction.response.edit_message(
                content="✅ **ВСЕ ДАННЫЕ СБРОШЕНЫ!**\n\nБот готов к работе с чистой базой данных.",
                embed=None,
                view=None
            )
        
        @discord.ui.button(label="❌ Отмена", style=discord.ButtonStyle.secondary)
        async def cancel(self, interaction: discord.Interaction, button: Button):
            await interaction.response.edit_message(
                content="❌ **СБРОС ОТМЕНЕН**\n\nДанные сохранены.",
                embed=None,
                view=None
            )
    
    embed = discord.Embed(
        title="⚠️ ⚠️ ⚠️ ОПАСНОЕ ДЕЙСТВИЕ ⚠️ ⚠️ ⚠️",
        description="Вы собираетесь **ПОЛНОСТЬЮ СБРОСИТЬ** все данные бота!",
        color=0xFF0000
    )
    
    embed.add_field(
        name="❌ Что будет удалено:",
        value="• Все члены семьи\n• Все заявки\n• Все предупреждения\n• Все мероприятия\n• Все кастомные ранги\n\n⚠️ **Это действие необратимо!**",
        inline=False
    )
    
    embed.add_field(
        name="📊 Текущая статистика:",
        value=f"• Членов: {len(bot.db.data['members'])}\n• Заявок: {len(bot.db.data['applications'])}\n• Предупреждений: {sum(len(w) for w in bot.db.data['warnings'].values())}\n• Мероприятий: {len(bot.db.data['events'])}\n• Рангов: {len(bot.db.data['ranks'])}",
        inline=False
    )
    
    view = ResetConfirmView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(
    name="сохранить",
    description="Принудительно сохранить все данные в файл"
)
@app_commands.default_permissions(administrator=True)
async def save_slash(interaction: discord.Interaction):
    """Сохранить данные в файл"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
        return
    
    try:
        bot.db.save_to_file()
        await interaction.response.send_message("✅ Данные успешно сохранены в файл!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка сохранения: {e}", ephemeral=True)

# ========== ЗАПУСК БОТА ==========

async def main():
    """Основная функция запуска"""
    print("\n🚀 ЗАПУСКАЕМ БОТА...")
    
    try:
        await bot.start(TOKEN)
    except discord.LoginFailure:
        print("\n❌ ОШИБКА: Неверный токен бота!")
        print("Пожалуйста, проверьте токен в переменной TOKEN")
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")

if __name__ == "__main__":
    # Запускаем бота
    asyncio.run(main())