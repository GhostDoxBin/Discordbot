"""
ПОЛНОСТЬЮ РАБОЧИЙ DISCORD БОТ SHINIGAMI С СЛЭШ-КОМАНДАМИ
"""

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import json
import os
from datetime import datetime
import asyncio

print("=" * 60)
print("🤖 DISCORD БОТ SHINIGAMI - СЛЭШ-КОМАНДЫ")
print("=" * 60)

# Настройки
TOKEN = "MTQ0NjEzMjc1Nzg1NTA3NjUyNw.GEnPhX.jye5IMrWS9dsX3IyvUXWQct1VkGfDEKXpyXx7Q"
FAMILY_NAME = "Shinigami"
GUILD_ID = 1446133863708360706  # ID вашего сервера
BOT_ID = 1446132757855076527    # ID вашего бота

print(f"✅ Используется токен: {TOKEN[:20]}...")
print(f"🏮 Сервер ID: {GUILD_ID}")
print(f"🤖 Бот ID: {BOT_ID}")
print(f"🔗 Ссылка для приглашения:")
print(f"https://discord.com/api/oauth2/authorize?client_id={BOT_ID}&permissions=8&scope=bot%20applications.commands")
print("=" * 60)

# Создаем бота с поддержкой слэш-команд
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
    
    async def setup_hook(self):
        """Настройка при запуске"""
        # Синхронизируем команды с сервером
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print("✅ Слэш-команды синхронизированы!")

bot = ShinigamiBot()

# Простая база данных в памяти
class SimpleDB:
    def __init__(self):
        self.data = {
            'members': {},
            'applications': {},
            'warnings': {},
            'events': {},
            'ranks': {
                'rank_1': {'name': 'Глава', 'color': '#000000'},
                'rank_2': {'name': 'Заместитель', 'color': '#FF0000'},
                'rank_3': {'name': 'Советник', 'color': '#800080'},
                'rank_4': {'name': 'Боец', 'color': '#FFFFFF'},
                'rank_5': {'name': 'Новичок', 'color': '#00FF00'}
            }
        }
    
    def get_member(self, user_id: str):
        return self.data['members'].get(str(user_id))
    
    def add_member(self, user_id: str, data: dict):
        self.data['members'][str(user_id)] = data
    
    def add_application(self, user_id: str, data: dict):
        self.data['applications'][str(user_id)] = data
    
    def get_pending_applications(self):
        return [app for app in self.data['applications'].values() if app.get('status') == 'pending']
    
    def add_warning(self, user_id: str, admin_id: str, reason: str):
        user_id = str(user_id)
        if user_id not in self.data['warnings']:
            self.data['warnings'][user_id] = []
        self.data['warnings'][user_id].append({
            'reason': reason,
            'admin_id': admin_id,
            'date': datetime.now().isoformat()
        })

db = SimpleDB()

# Модальное окно для заявки
class ApplicationModal(Modal):
    def __init__(self):
        super().__init__(title=f"📋 Заявка в {FAMILY_NAME}")
        
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
        try:
            age = int(self.age.value)
            level = int(self.level.value)
            
            if age < 14:
                await interaction.response.send_message(
                    "❌ Минимальный возраст - 14 лет.",
                    ephemeral=True
                )
                return
            
            if level < 3:
                await interaction.response.send_message(
                    "❌ Минимальный уровень - 3.",
                    ephemeral=True
                )
                return
            
            # Проверяем, не является ли уже членом
            if db.get_member(str(interaction.user.id)):
                await interaction.response.send_message(
                    "✅ Вы уже член семьи!",
                    ephemeral=True
                )
                return
            
            # Проверяем, не подана ли уже заявка
            existing_app = db.data['applications'].get(str(interaction.user.id))
            if existing_app and existing_app.get('status') == 'pending':
                await interaction.response.send_message(
                    "📝 Ваша заявка уже на рассмотрении!",
                    ephemeral=True
                )
                return
            
            # Сохраняем заявку
            db.add_application(str(interaction.user.id), {
                'user_id': str(interaction.user.id),
                'username': str(interaction.user),
                'full_name': interaction.user.display_name,
                'age': age,
                'level': level,
                'game_name': self.game_name.value,
                'experience': self.experience.value,
                'reason': self.reason.value,
                'status': 'pending',
                'date': datetime.now().isoformat()
            })
            
            await interaction.response.send_message(
                "✅ Заявка отправлена!\nОжидайте решения администрации.",
                ephemeral=True
            )
            
        except ValueError:
            await interaction.response.send_message(
                "❌ Пожалуйста, введите корректные числа для возраста и уровня!",
                ephemeral=True
            )

# ========== СЛЭШ-КОМАНДЫ ==========

@bot.tree.command(
    name="заявка",
    description="Подать заявку на вступление в семью Shinigami"
)
async def apply_slash(interaction: discord.Interaction):
    """Слэш-команда подачи заявки"""
    # Проверяем, не является ли уже членом
    if db.get_member(str(interaction.user.id)):
        await interaction.response.send_message(
            "✅ Вы уже член семьи!",
            ephemeral=True
        )
        return
    
    # Проверяем, не подана ли уже заявка
    existing_app = db.data['applications'].get(str(interaction.user.id))
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
        value="• `/заявка` - Подать заявку\n• `/статистика` - Статистика семьи\n• `/правила` - Правила семьи\n• `/члены` - Список членов\n• `/профиль` - Ваш профиль\n• `/ранги` - Ранги семьи",
        inline=False
    )
    
    embed.add_field(
        name="📨 Для вступления:",
        value="Используйте команду `/заявка` для подачи заявки",
        inline=False
    )
    
    if interaction.user.guild_permissions.administrator:
        embed.add_field(
            name="⚙️ Админ команды:",
            value="• `/админ` - Админ панель\n• `/заявки` - Просмотр заявок\n• `/предупредить` - Выдать варн\n• `/принять` - Принять заявку\n• `/отклонить` - Отклонить заявку",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="статистика",
    description="Статистика семьи Shinigami"
)
async def stats_slash(interaction: discord.Interaction):
    """Слэш-команда статистики"""
    members = len(db.data['members'])
    apps = len(db.get_pending_applications())
    warns = sum(len(w) for w in db.data['warnings'].values())
    
    embed = discord.Embed(
        title=f"📊 Статистика семьи {FAMILY_NAME}",
        color=0x800080,
        timestamp=datetime.now()
    )
    
    embed.add_field(name="👥 Членов", value=str(members), inline=True)
    embed.add_field(name="📨 Заявок", value=str(apps), inline=True)
    embed.add_field(name="⚠️ Варнов", value=str(warns), inline=True)
    embed.add_field(name="🎖️ Рангов", value="5", inline=True)
    embed.add_field(name="📅 Событий", value=str(len(db.data['events'])), inline=True)
    
    # Распределение по рангам
    rank_counts = {}
    for member in db.data['members'].values():
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
    if not db.data['members']:
        await interaction.response.send_message("👥 В семье пока нет членов.")
        return
    
    embed = discord.Embed(
        title=f"👥 Члены семьи {FAMILY_NAME}",
        color=0x800080
    )
    
    for i, (user_id, member) in enumerate(list(db.data['members'].items())[:10], 1):
        embed.add_field(
            name=f"{i}. {member.get('game_name', 'Без имени')}",
            value=f"🎖️ {member.get('rank', 'Новичок')} | 🎮 Ур. {member.get('level', 0)}",
            inline=False
        )
    
    if len(db.data['members']) > 10:
        embed.set_footer(text=f"Всего членов: {len(db.data['members'])}")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="профиль",
    description="Просмотр профиля участника"
)
@app_commands.describe(участник="Участник для просмотра профиля (необязательно)")
async def profile_slash(interaction: discord.Interaction, участник: discord.Member = None):
    """Слэш-команда профиля"""
    target = участник or interaction.user
    member_data = db.get_member(str(target.id))
    
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
        embed.add_field(name="📅 В семье с", value=member_data.get('join_date', 'Недавно')[:10], inline=True)
        embed.add_field(name="🎂 Возраст", value=str(member_data.get('age', 0)), inline=True)
        embed.add_field(name="🎮 Уровень", value=str(member_data.get('level', 0)), inline=True)
    else:
        embed.description = "❌ Не является членом семьи"
    
    embed.add_field(name="🆔 Discord ID", value=target.id, inline=True)
    
    # Добавляем информацию о предупреждениях
    warnings = db.data['warnings'].get(str(target.id), [])
    if warnings:
        embed.add_field(
            name="⚠️ Предупреждения",
            value=f"Всего: {len(warnings)}",
            inline=True
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
    
    ranks = db.data['ranks']
    for rank_id, rank_data in ranks.items():
        embed.add_field(
            name=rank_data['name'],
            value=f"Цвет: {rank_data['color']}",
            inline=True
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="мой_ранг",
    description="Показать ваш текущий ранг в семье"
)
async def myrank_slash(interaction: discord.Interaction):
    """Слэш-команда моего ранга"""
    member_data = db.get_member(str(interaction.user.id))
    
    if not member_data:
        await interaction.response.send_message(
            "❌ Вы не являетесь членом семьи.",
            ephemeral=True
        )
        return
    
    rank = member_data.get('rank', 'Новичок')
    rank_name = rank
    
    embed = discord.Embed(
        title=f"🎖️ Ваш ранг: {rank_name}",
        color=0x00FF00
    )
    
    if rank == "Глава":
        embed.description = "👑 У вас полный доступ ко всем функциям!"
        embed.add_field(name="Права", value="• Управление всеми членами\n• Принятие/отклонение заявок\n• Создание событий\n• Выдача предупреждений", inline=False)
    elif rank == "Заместитель":
        embed.description = "🎖️ Вы можете управлять членами и заявками."
        embed.add_field(name="Права", value="• Принятие/отклонение заявок\n• Выдача предупреждений\n• Просмотр статистики", inline=False)
    elif rank == "Советник":
        embed.description = "⭐ Вы можете управлять заявками и модерировать."
        embed.add_field(name="Права", value="• Принятие/отклонение заявок\n• Просмотр статистики\n• Модерация чата", inline=False)
    elif rank == "Боец":
        embed.description = "⚔️ Вы можете просматривать статистику и участвовать в событиях."
        embed.add_field(name="Права", value="• Просмотр статистики\n• Участие в событиях\n• Общение в чате", inline=False)
    else:
        embed.description = "🌱 Вы новичок в семье. Активно участвуйте в жизни семьи для повышения!"
        embed.add_field(name="Права", value="• Просмотр правил\n• Общение в чате\n• Участие в событиях", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="события",
    description="Показать ближайшие события семьи"
)
async def events_slash(interaction: discord.Interaction):
    """Слэш-команда событий"""
    events = db.data['events']
    
    if not events:
        await interaction.response.send_message("📭 Нет запланированных событий.")
        return
    
    embed = discord.Embed(
        title=f"📅 События семьи {FAMILY_NAME}",
        color=0x800080
    )
    
    for i, (event_id, event) in enumerate(list(events.items())[:5], 1):
        embed.add_field(
            name=f"{i}. {event.get('title', 'Без названия')}",
            value=f"📅 {event.get('date', 'Дата не указана')}\n📝 {event.get('description', 'Без описания')[:100]}...",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

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
    
    members = len(db.data['members'])
    apps = len(db.get_pending_applications())
    warns = sum(len(w) for w in db.data['warnings'].values())
    
    embed = discord.Embed(
        title=f"⚙️ Админ панель {FAMILY_NAME}",
        color=0xFF0000,
        timestamp=datetime.now()
    )
    
    embed.add_field(name="👥 Членов", value=str(members), inline=True)
    embed.add_field(name="📨 Заявок", value=str(apps), inline=True)
    embed.add_field(name="⚠️ Варнов", value=str(warns), inline=True)
    embed.add_field(name="🎖️ Рангов", value="5", inline=True)
    
    embed.add_field(
        name="📋 Админ команды:",
        value="• `/заявки` - Просмотр заявок\n• `/принять` - Принять заявку\n• `/отклонить` - Отклонить заявку\n• `/предупредить` - Выдать варн",
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
    
    apps = db.get_pending_applications()
    
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
    
    await interaction.response.send_message(embed=embed)

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
    if not db.get_member(str(участник.id)):
        await interaction.response.send_message(f"❌ {участник.mention} не является членом семьи!", ephemeral=True)
        return
    
    # Добавляем предупреждение
    db.add_warning(str(участник.id), str(interaction.user.id), причина)
    
    # Считаем количество предупреждений
    warnings = db.data['warnings'].get(str(участник.id), [])
    warn_count = len(warnings)
    
    embed = discord.Embed(
        title="⚠️ Предупреждение выдано",
        description=f"{участник.mention} получил предупреждение!",
        color=0xffa500
    )
    
    embed.add_field(name="Причина", value=причина, inline=False)
    embed.add_field(name="Всего предупреждений", value=str(warn_count), inline=True)
    embed.add_field(name="Выдал", value=interaction.user.display_name, inline=True)
    
    await interaction.response.send_message(embed=embed)
    
    # Отправляем личное сообщение
    try:
        await участник.send(f"⚠️ Вы получили предупреждение на сервере **{interaction.guild.name}**\n**Причина:** {причина}\n**Всего предупреждений:** {warn_count}")
    except:
        pass

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
    applications = db.data['applications']
    
    if user_id not in applications or applications[user_id].get('status') != 'pending':
        await interaction.response.send_message("❌ Заявка не найдена или уже рассмотрена!", ephemeral=True)
        return
    
    application = applications[user_id]
    rank_value = ранг.value
    
    # Добавляем в члены
    db.add_member(user_id, {
        'user_id': user_id,
        'username': application.get('username', ''),
        'full_name': application.get('full_name', ''),
        'game_name': application.get('game_name', ''),
        'rank': rank_value,
        'join_date': datetime.now().isoformat(),
        'level': application.get('level', 0),
        'age': application.get('age', 0)
    })
    
    # Обновляем статус заявки
    applications[user_id]['status'] = 'accepted'
    
    # Пытаемся выдать роль
    try:
        role_name = rank_value
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if not role:
            role = await interaction.guild.create_role(
                name=role_name,
                color=discord.Color.default(),
                mentionable=True
            )
        await участник.add_roles(role)
    except Exception as e:
        print(f"Ошибка при выдаче роли: {e}")
    
    embed = discord.Embed(
        title="✅ Заявка принята",
        description=f"Пользователь {участник.mention} принят в семью!",
        color=0x00FF00
    )
    
    embed.add_field(name="🎖️ Ранг", value=rank_value, inline=True)
    embed.add_field(name="✅ Принял", value=interaction.user.display_name, inline=True)
    
    await interaction.response.send_message(embed=embed)
    
    # Уведомляем пользователя
    try:
        await участник.send(f"🎉 Поздравляем! Ваша заявка в семью {FAMILY_NAME} принята!\nВаш ранг: {rank_value}")
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
    applications = db.data['applications']
    
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

# ========== СОБЫТИЯ БОТА ==========

@bot.event
async def on_ready():
    print(f"\n{'=' * 60}")
    print(f"✅ БОТ {bot.user} ЗАПУЩЕН!")
    print(f"🆔 ID: {bot.user.id}")
    print(f"🏮 Семья: {FAMILY_NAME}")
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print(f"{'=' * 60}")
    
    # Показываем список зарегистрированных команд
    commands_list = await bot.tree.fetch_commands()
    print(f"📋 Зарегистрировано слэш-команд: {len(commands_list)}")
    for cmd in commands_list:
        print(f"  • /{cmd.name} - {cmd.description}")
    print(f"{'=' * 60}")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"семью {FAMILY_NAME}"
        )
    )

# Обработка сообщений
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Если сообщение содержит только слэш - показываем меню
    if message.content.strip() == "/":
        view = View(timeout=60)
        
        # Кнопка подачи заявки
        apply_button = Button(label="📋 Подать заявку", style=discord.ButtonStyle.success)
        
        async def apply_callback(interaction):
            modal = ApplicationModal()
            await interaction.response.send_modal(modal)
        
        apply_button.callback = apply_callback
        view.add_item(apply_button)
        
        # Кнопка статистики
        stats_button = Button(label="📊 Статистика", style=discord.ButtonStyle.primary)
        
        async def stats_callback(interaction):
            members = len(db.data['members'])
            apps = len(db.get_pending_applications())
            warns = sum(len(w) for w in db.data['warnings'].values())
            
            embed = discord.Embed(
                title=f"📊 Статистика семьи {FAMILY_NAME}",
                color=0x800080
            )
            embed.add_field(name="👥 Членов", value=str(members), inline=True)
            embed.add_field(name="📨 Заявок", value=str(apps), inline=True)
            embed.add_field(name="⚠️ Варнов", value=str(warns), inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        stats_button.callback = stats_callback
        view.add_item(stats_button)
        
        # Кнопка членов
        members_button = Button(label="👥 Члены", style=discord.ButtonStyle.secondary)
        
        async def members_callback(interaction):
            if not db.data['members']:
                await interaction.response.send_message("👥 В семье пока нет членов.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"👥 Члены семьи {FAMILY_NAME}",
                color=0x800080
            )
            
            for i, (user_id, member) in enumerate(list(db.data['members'].items())[:10], 1):
                embed.add_field(
                    name=f"{i}. {member.get('game_name', 'Без имени')}",
                    value=f"🎖️ {member.get('rank', 'Новичок')}",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        members_button.callback = members_callback
        view.add_item(members_button)
        
        # Кнопка профиля
        profile_button = Button(label="👤 Профиль", style=discord.ButtonStyle.success)
        
        async def profile_callback(interaction):
            member_data = db.get_member(str(interaction.user.id))
            
            embed = discord.Embed(
                title=f"👤 Профиль {interaction.user.display_name}",
                color=interaction.user.color if interaction.user.color != discord.Color.default() else 0x000000
            )
            
            if interaction.user.avatar:
                embed.set_thumbnail(url=interaction.user.avatar.url)
            
            if member_data:
                embed.add_field(name="🎮 Игровой ник", value=member_data.get('game_name', 'Не указан'), inline=True)
                embed.add_field(name="🎖️ Ранг", value=member_data.get('rank', 'Новичок'), inline=True)
                embed.add_field(name="📅 В семье с", value=member_data.get('join_date', 'Недавно')[:10], inline=True)
            else:
                embed.description = "❌ Не является членом семьи"
            
            embed.add_field(name="🆔 Discord ID", value=interaction.user.id, inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        profile_button.callback = profile_callback
        view.add_item(profile_button)
        
        # Кнопка правил
        rules_button = Button(label="📜 Правила", style=discord.ButtonStyle.secondary)
        
        async def rules_callback(interaction):
            embed = discord.Embed(
                title=f"📜 Правила семьи {FAMILY_NAME}",
                color=0xFF0000
            )
            
            rules = [
                "1. Уважение к каждому члену семьи",
                "2. Активность в играх и общении",
                "3. Помощь новичкам и поддержка товарищей",
                "4. Исполнение приказов руководства"
            ]
            
            embed.description = "\n".join(rules)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        rules_button.callback = rules_callback
        view.add_item(rules_button)
        
        # Кнопка для админов
        if message.author.guild_permissions.administrator:
            admin_button = Button(label="⚙️ Админ", style=discord.ButtonStyle.danger)
            
            async def admin_callback(interaction):
                members = len(db.data['members'])
                apps = len(db.get_pending_applications())
                warns = sum(len(w) for w in db.data['warnings'].values())
                
                embed = discord.Embed(
                    title="⚙️ Админ панель",
                    color=0xFF0000
                )
                
                embed.add_field(name="👥 Членов", value=str(members), inline=True)
                embed.add_field(name="📨 Заявок", value=str(apps), inline=True)
                embed.add_field(name="⚠️ Варнов", value=str(warns), inline=True)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            admin_button.callback = admin_callback
            view.add_item(admin_button)
        
        embed = discord.Embed(
            title=f"🏮 {FAMILY_NAME} - Главное меню",
            description="Выберите действие:\n\n**ИЛИ используйте слэш-команды:**\n`/заявка` `/старт` `/статистика` `/правила` `/члены` `/профиль`",
            color=0x000000
        )
        
        await message.channel.send(embed=embed, view=view)
        return
    
    await bot.process_commands(message)

# Обработка ошибок
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ У вас нет прав для выполнения этой команды!")
        return
    
    print(f"❌ Ошибка команды: {error}")

# Обработка ошибок слэш-команд
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    print(f"❌ Ошибка слэш-команды: {error}")
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("⛔ У вас нет прав для этой команды!", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Ошибка: {str(error)[:100]}", ephemeral=True)

# Запуск бота
if __name__ == "__main__":
    print("🚀 Запуск бота со слэш-командами...")
    print("⏳ Команды появятся через несколько секунд после запуска...")
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except discord.errors.LoginFailure:
        print("❌ Ошибка: Неверный токен!")
        print("📝 Проверьте что токен правильный и бот добавлен на сервер")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()